#!/usr/bin/env python3
"""Invoke a cataloged Amazon operation through the Nexscope gateway."""
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, quote, urlencode
from urllib.request import Request, urlopen

BASE = os.environ.get("NEXSCOPE_PROXY_BASE", "").strip().rstrip("/")
KEY = os.environ.get("NEXSCOPE_API_KEY", "").strip()
MAX_RESPONSE_BYTES = 32 * 1024 * 1024
CATALOG = json.loads((Path(__file__).parent.parent / "references" / "api.json").read_text(encoding="utf-8"))
OPERATIONS = {item["id"]: item for item in CATALOG["operations"]}

def arguments():
    if len(sys.argv) != 2:
        raise ValueError("Provide exactly one JSON object argument")
    value = json.loads(sys.argv[1])
    if not isinstance(value, dict):
        raise ValueError("The argument must be a JSON object")
    return value

def unwrap(value):
    if not isinstance(value, dict):
        raise RuntimeError("Gateway response must be a JSON object")
    if "code" in value:
        if value.get("code") != 0:
            raise RuntimeError("Gateway application failure")
        value = value.get("data")
    if not isinstance(value, dict): return value
    if value.get("success") is False or value.get("error"):
        raise RuntimeError("Upstream failure")
    response = value.get("response")
    status = response.get("httpStatus") if isinstance(response, dict) else value.get("httpStatus")
    if isinstance(status, int) and status >= 400:
        raise RuntimeError(f"Upstream returned HTTP {status}")
    if isinstance(response, dict) and "payload" in response:
        payload = response.get("payload")
        metadata = {"httpStatus": status}
        for key in ("requestId", "rateLimit", "nextToken"):
            if value.get(key) is not None: metadata[key] = value[key]
        if isinstance(payload, dict): return {**payload, "_gateway": metadata}
        return {"content": payload, "_gateway": metadata}
    return value

def call(route, body, timeout=90):
    if not BASE or not KEY:
        raise ValueError("NEXSCOPE_PROXY_BASE and NEXSCOPE_API_KEY are required")
    request = Request(BASE + route, data=json.dumps(body).encode(), headers={
        "Authorization": "Bearer " + KEY, "Content-Type": "application/json", "Accept": "application/json",
    }, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            raw_bytes = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw_bytes) > MAX_RESPONSE_BYTES: raise RuntimeError("Gateway response exceeds 32 MiB limit")
            raw = raw_bytes.decode("utf-8")
    except HTTPError as error:
        raise RuntimeError(f"Gateway HTTP {error.code}") from error
    except URLError as error:
        raise RuntimeError("Gateway request failed") from error
    try:
        return unwrap(json.loads(raw))
    except json.JSONDecodeError as error:
        raise RuntimeError("Gateway returned non-JSON content") from error

def resolve_path(template, values):
    result = template
    for key, value in values.items():
        result = result.replace("{" + key + "}", quote(str(value), safe=""))
    if "{" in result or result.startswith("opaque") or result.startswith("backend-owned"):
        raise ValueError("The selected operation requires its specialized workflow or missing path parameters")
    return result

def recursive_field(value, key, depth=0):
    if depth > 20:
        return None
    if isinstance(value, dict):
        if value.get(key) is not None: return value[key]
        for nested in ("payload", "response", "data"):
            nested_value = value.get(nested)
            if isinstance(nested_value, list):
                # List field (SD API returns a bare array): return it directly as the result
                return nested_value
            found = recursive_field(nested_value, key, depth + 1)
            if found is not None:
                return found
    return None

def add_token(query, token):
    pairs = parse_qsl(query or "", keep_blank_values=True)
    pairs = [(key, value) for key, value in pairs if key not in {"nextToken", "next_token"}]
    pairs.append(("nextToken", str(token)))
    return urlencode(pairs)

def set_query_value(query, key, value):
    pairs = [(item_key, item_value) for item_key, item_value in parse_qsl(query or "", keep_blank_values=True) if item_key != key]
    pairs.append((key, str(value)))
    return urlencode(pairs)

def named_list_length(value, key):
    found = recursive_field(value, key)
    return len(found) if isinstance(found, list) else 0

def filter_values(value):
    if isinstance(value, dict):
        if set(value) - {"include", "queryTermMatchType"} or not isinstance(value.get("include"),list): raise ValueError("Filter wrappers must contain an include array")
        value = value.get("include", [])
    if not isinstance(value, list):
        value = [value]
    if any(isinstance(item,(dict,list)) for item in value): raise ValueError("Filter values must be scalars")
    return [str(item) for item in value if item is not None]

def validate_operation_inputs(operation, params):
    for group in operation.get("mutuallyExclusiveGroups", []):
        present=[field for field in group if params.get(field) is not None]
        if len(present)>1: raise ValueError("Mutually exclusive inputs: " + ", ".join(group))
    for field,dependencies in operation.get("dependentInputs",{}).items():
        if params.get(field) is not None:
            missing=[dependency for dependency in dependencies if params.get(dependency) is None]
            if missing: raise ValueError(field+" requires "+", ".join(missing))
    for field,limit in operation.get("maxItems",{}).items():
        value=params.get(field)
        if value is None: continue
        if isinstance(value,list):
            if not value or any(isinstance(item,(dict,list)) or item is None for item in value): raise ValueError(field+" must contain scalar values")
            count=len(value)
        elif isinstance(value,(str,int)) and not isinstance(value,bool): count=1
        else: raise ValueError(field+" must be a scalar or array of scalars")
        if count>limit: raise ValueError(f"{field} accepts at most {limit} values")
    for field,bounds in operation.get("numericRanges",{}).items():
        value=params.get(field)
        if value is None: continue
        if isinstance(value,bool) or not isinstance(value,int) or not bounds[0]<=value<=bounds[1]:
            raise ValueError(f"{field} must be an integer from {bounds[0]} to {bounds[1]}")
    for field,allowed in operation.get("enumInputs",{}).items():
        value=params.get(field)
        if value is not None and value not in allowed: raise ValueError(field+" must be one of: "+", ".join(allowed))
    for selector,mapping in operation.get("conditionalInputs",{}).items():
        selected=params.get(selector); rule=mapping.get(selected)
        if rule is None: continue
        missing=[field for field in rule.get("required",[]) if params.get(field) is None]
        forbidden=[field for field in rule.get("forbidden",[]) if params.get(field) is not None]
        if missing: raise ValueError(str(selected)+" requires "+", ".join(missing))
        if forbidden: raise ValueError(str(selected)+" cannot be combined with "+", ".join(forbidden))

def apply_client_filters(value, result_key, filters, targets):
    if not filters or not isinstance(value, dict):
        return value
    items = recursive_field(value, result_key)
    if not isinstance(items, list):
        return value
    filtered = items
    server_total = len(items)
    for input_name, wanted in filters.items():
        field = targets[input_name]
        accepted = set(wanted)
        filtered = [item for item in filtered if isinstance(item, dict) and item.get(field) in accepted]
    stack=[(value,0)]; replaced=False; seen=set()
    while stack:
        node,depth=stack.pop()
        if not isinstance(node,dict) or id(node) in seen: continue
        seen.add(id(node))
        if depth>20: raise RuntimeError("Gateway response nesting exceeds the supported limit")
        if isinstance(node.get(result_key),list): node[result_key]=filtered; replaced=True; break
        for key in ("payload","response","data"):
            if isinstance(node.get(key),dict): stack.append((node[key],depth+1))
    if not replaced: return value
    value["serverTotalBeforeClientFilter"] = server_total
    value["clientSideFilters"] = filters
    return value

def encoded_query(operation, params):
    explicit = params.pop("queryString", None)
    if explicit is not None:
        if not isinstance(explicit,str): raise ValueError("queryString must be a string")
        return explicit
    pairs = []
    parameter_map = operation.get("queryParameterMap", {})
    comma_inputs = set(operation.get("commaSeparatedQueryInputs", []))
    first_only = set(operation.get("firstOnlyQueryInputs", []))
    sd_modes = operation.get("sdFilterModes", {})
    for key in operation.get("queryInputs", []):
        if key not in params or params[key] is None:
            continue
        value = params[key]
        if sd_modes.get(key) == "first": values = filter_values(value)[:1]
        elif sd_modes.get(key) == "comma-lower": values = [",".join(item.lower() for item in filter_values(value))]
        elif sd_modes.get(key) == "comma": values = [",".join(filter_values(value))]
        elif isinstance(value, list) and key in first_only: values = value[:1]
        elif isinstance(value, list) and key in comma_inputs: values = [",".join(str(item) for item in value)]
        else: values = value if isinstance(value, list) else [value]
        for item in values:
            if isinstance(item, (dict, list)):
                item = json.dumps(item, separators=(",", ":"))
            pairs.append((parameter_map.get(key, key), str(item)))
    return urlencode(pairs) if pairs else None

def request_body(operation, params):
    if "body" in params:
        value=params.pop("body")
        if not isinstance(value,(dict,list)): raise ValueError("body must be an object or array")
        return value
    if "payload" in params:
        value=params.pop("payload")
        if not isinstance(value,(dict,list)): raise ValueError("payload must be an object or array")
        return value
    direct = operation.get("directBodyInput")
    if direct and direct in params:
        return params[direct]
    wrapper = operation.get("bodyWrapper")
    if wrapper and wrapper in params:
        if not isinstance(params[wrapper],dict): raise ValueError(wrapper+" must be an object")
        return {wrapper: params[wrapper]}
    body = {key: params[key] for key in operation.get("bodyInputs", []) if key in params}
    transformer = operation.get("batchTransformer")
    if transformer:
        body = transform_batch(transformer, body.get("requests"), bool(params.get("useAmazonRequestShape")), operation.get("batchMaxItems", 20))
    return body

def transform_batch(kind, requests, native=False, max_items=20):
    if not isinstance(requests, list) or not 1 <= len(requests) <= max_items:
        raise ValueError(f"requests must contain 1 to {max_items} objects")
    if native: return {"requests": requests}
    output = []
    for item in requests:
        if not isinstance(item, dict): raise ValueError("each batch request must be an object")
        if kind in {"itemOffers", "listingOffers"}:
            identifier_key = "asin" if kind == "itemOffers" else "sku"
            identifier = str(item.get(identifier_key) or "").strip(); marketplace = str(item.get("marketplaceId") or "").strip(); condition = str(item.get("itemCondition") or "").strip()
            if not identifier or not marketplace or not condition: raise ValueError(f"each request needs {identifier_key}, marketplaceId, and itemCondition")
            segment = "items" if kind == "itemOffers" else "listings"
            row = {"uri": f"/products/pricing/v0/{segment}/{quote(identifier, safe='')}/offers", "method": "GET", "MarketplaceId": marketplace, "ItemCondition": condition}
            if item.get("customerType"): row["CustomerType"] = str(item["customerType"]).strip()
            if item.get("headers") is not None: row["headers"] = item["headers"]
        elif kind == "competitiveSummary":
            asin = str(item.get("asin") or "").strip(); marketplace = str(item.get("marketplaceId") or "").strip(); included = item.get("includedData")
            if not asin or not marketplace or not isinstance(included, list) or not included: raise ValueError("each request needs asin, marketplaceId, and non-empty includedData")
            row = {"uri": "/products/pricing/2022-05-01/items/competitiveSummary", "method": "POST", "asin": asin, "marketplaceId": marketplace, "includedData": included}
            if "lowestPricedOffersInputs" in item: row["lowestPricedOffersInputs"] = item["lowestPricedOffersInputs"]
        else:
            marketplace = str(item.get("marketplaceId") or "").strip(); sku = str(item.get("sku") or "").strip()
            if not marketplace or not sku or not isinstance(item.get("segment"), dict): raise ValueError("each request needs marketplaceId, sku, and segment")
            row = {"uri": "/products/pricing/2022-05-01/offer/featuredOfferExpectedPrice", "method": "POST", "marketplaceId": marketplace, "sku": sku, "segment": item["segment"]}
        output.append(row)
    return {"requests": output}

def main():
    params = arguments()
    operation_id = str(params.pop("operation", "")).strip()
    operation = OPERATIONS.get(operation_id)
    if not operation:
        raise ValueError("Unknown operation; select an id from references/api.json")
    if not operation.get("callable", True):
        raise ValueError("This legacy-only mechanism is not callable; use the documented backend-owned replacement")
    if operation.get("executionMode", "generic") != "generic":
        script = operation.get("specializedScript") or "the dedicated workflow script"
        raise ValueError("This operation requires " + script + " as documented in api.md")
    phase_value=params.pop("phase","read")
    if not isinstance(phase_value,str): raise ValueError("phase must be a string")
    phase = phase_value.lower()
    missing = [key for key in operation["requiredInputs"] if key not in params]
    if missing:
        raise ValueError("Missing required inputs: " + ", ".join(missing))
    connection_id=params.get("connectionId")
    if isinstance(connection_id,bool) or not isinstance(connection_id,(int,str)) or not str(connection_id).strip(): raise ValueError("connectionId must be a non-empty string or integer")
    input_sets = operation.get("requiredInputSets", [])
    if input_sets and not any(all(params.get(key) is not None for key in option) for option in input_sets):
        choices = [" + ".join(option) for option in input_sets]
        raise ValueError("Provide one complete input set: " + " or ".join(choices))
    validate_operation_inputs(operation,params)
    for key, value in operation.get("defaults", {}).items():
        params.setdefault(key, value)
    raw_path_params=params.pop("pathParams",{})
    if not isinstance(raw_path_params,dict): raise ValueError("pathParams must be an object")
    path_params = dict(raw_path_params)
    path_params.update(params)
    for key in operation.get("pathInputs",[]):
        if isinstance(path_params.get(key),(dict,list,bool)) or path_params.get(key) is None: raise ValueError(key+" must be a scalar path value")
    provider_path = operation["providerPath"]
    if params.pop("includeExtendedDataFields", False) and operation.get("extendedProviderPath"):
        provider_path = operation["extendedProviderPath"]
    path = resolve_path(provider_path, path_params)
    body = request_body(operation, params)
    workspace_id = params.pop("workspaceId", None)
    common = {"connectionId": params.pop("connectionId"),
              "method": operation["method"], "path": path, "queryString": encoded_query(operation, params),
              "requestId": params.pop("requestId", None)}
    if workspace_id:
        common["workspaceId"] = workspace_id
    if operation.get("contentType"):
        common["contentType"] = operation["contentType"]
    if operation["mutation"]:
        if phase not in {"preview", "confirm"}:
            raise ValueError("Mutations require phase=preview, then explicit approval, then phase=confirm")
        common["body"] = body
        route = "/api/skill/amazon/" + ("ads/" if operation["product"] in {"SP", "SB", "SD"} else "seller/") + "write-" + phase
        if phase == "confirm":
            token = params.pop("confirmationToken", None)
            if not isinstance(token,str) or not token:
                raise ValueError("confirmationToken is required after exact user approval")
            common["confirmationToken"] = token
        result = call(route, common)
    else:
        is_ads = operation["product"] in {"SP", "SB", "SD"}
        if is_ads:
            common["body"] = body
        route = "/api/skill/amazon/" + ("ads/read" if is_ads else "seller/read")
        pagination = operation.get("pagination") or {}
        client_filters = {key: filter_values(params[key]) for key in operation.get("clientSideFilters", {}) if params.get(key) is not None}
        fetch_all_value=params.pop("fetchAll",pagination.get("defaultFetchAll",False))
        if type(fetch_all_value) is not bool: raise ValueError("fetchAll must be true or false")
        fetch_all=fetch_all_value
        max_pages_value=params.pop("maxPages",20)
        if isinstance(max_pages_value,bool) or not isinstance(max_pages_value,int) or not 1<=max_pages_value<=100: raise ValueError("maxPages must be an integer from 1 to 100")
        max_pages=max_pages_value
        pages = []
        seen_tokens = set()
        offset = 0
        page_size=pagination.get("defaultPageSize",100)
        if pagination.get("mode") == "offset-query":
            page_size=params.get("maxResults",page_size)
            if isinstance(page_size,bool) or not isinstance(page_size,int) or not 1<=page_size<=100: raise ValueError("maxResults must be an integer from 1 to 100")
            common["queryString"] = set_query_value(common.get("queryString"), pagination["startIndexField"], 0)
            common["queryString"] = set_query_value(common.get("queryString"), pagination["pageSizeField"], page_size)
        while True:
            page = call(route, common)
            provider_page_length = named_list_length(page, pagination.get("resultField"))
            pages.append(apply_client_filters(page, pagination.get("resultField"), client_filters, operation.get("clientSideFilters", {})))
            token = recursive_field(page, pagination.get("responseTokenField", "nextToken"))
            if token is not None:
                token_key = str(token)
                if token_key in seen_tokens: raise RuntimeError("Pagination returned a repeated token")
                seen_tokens.add(token_key)
            offset_more = pagination.get("mode") == "offset-query" and provider_page_length >= page_size
            if not fetch_all or (not token and not offset_more) or len(pages) >= max_pages:
                break
            if token and pagination.get("mode") == "next-token-body":
                common.setdefault("body", {})[pagination.get("requestTokenField", "nextToken")] = token
            elif token:
                common["queryString"] = set_query_value(common.get("queryString"), pagination.get("requestTokenField", "nextToken"), token)
            else:
                offset += provider_page_length
                common["queryString"] = set_query_value(common.get("queryString"), pagination["startIndexField"], offset)
        has_more=bool(token or offset_more)
        if len(pages)==1:
            result=pages[0]
        else:
            result={"pages":pages,"nextToken":recursive_field(pages[-1],pagination.get("responseTokenField","nextToken"))}
        if pagination:
            total=sum(named_list_length(page,pagination.get("resultField")) for page in pages) if pagination.get("resultField") else None
            metadata={"success":True,"pagesFetched":len(pages),"truncated":has_more}
            if total is not None: metadata["total"]=total
            if isinstance(result,dict):
                for key,value in metadata.items(): result.setdefault(key,value)
            else: result={"data":result,**metadata}
    print(json.dumps(result, indent=2, ensure_ascii=True))

if __name__ == "__main__":
    try:
        main()
    except (KeyError, OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        raise SystemExit(1)
