#!/usr/bin/env python3
"""Run an Amazon Ads v3 report workflow through a backend-owned Ads connection."""
import base64, json, os, socket, stat, sys, tempfile, time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = os.environ.get("NEXSCOPE_PROXY_BASE", "").strip().rstrip("/")
KEY = os.environ.get("NEXSCOPE_API_KEY", "").strip()
MAX_CONTENT_BYTES = 20 * 1024 * 1024
MAX_ENCODED_BYTES = ((MAX_CONTENT_BYTES + 2) // 3) * 4
MAX_RESPONSE_BYTES = 32 * 1024 * 1024

def unwrap(value):
    if not isinstance(value, dict) or value.get("code") != 0:
        raise RuntimeError("Gateway application failure" if isinstance(value, dict) else "Invalid gateway response")
    data = value.get("data")
    if isinstance(data, dict) and (data.get("error") or data.get("success") is False):
        raise RuntimeError("Upstream failure")
    response = data.get("response") if isinstance(data, dict) else None
    status = response.get("httpStatus") if isinstance(response, dict) else data.get("httpStatus") if isinstance(data, dict) else None
    if isinstance(status, int) and status >= 400: raise RuntimeError(f"Upstream returned HTTP {status}")
    if isinstance(response, dict) and "payload" in response:
        payload=response.get("payload"); meta={"httpStatus":status}
        return {**payload,"_gateway":meta} if isinstance(payload,dict) else {"content":payload,"_gateway":meta}
    return data

def find_field(value, key, depth=0):
    if depth > 20: return None
    if isinstance(value, dict):
        if value.get(key) is not None: return value[key]
        for nested in ("payload","response","data","document"):
            found=find_field(value.get(nested),key,depth+1)
            if found is not None: return found
    return None

def call(route, body, timeout=300, deadline=None):
    if not BASE or not KEY: raise ValueError("NEXSCOPE_PROXY_BASE and NEXSCOPE_API_KEY are required")
    if deadline is not None:
        remaining=deadline-time.monotonic()
        if remaining<=0: raise TimeoutError("Polling deadline reached")
        timeout=min(float(timeout),remaining)
    request = Request(BASE + route, data=json.dumps(body).encode(), headers={"Authorization": "Bearer " + KEY,
        "Content-Type": "application/json", "Accept": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            raw=response.read(MAX_RESPONSE_BYTES+1)
            if len(raw)>MAX_RESPONSE_BYTES: raise RuntimeError("Gateway response exceeds 32 MiB limit")
            return unwrap(json.loads(raw.decode("utf-8")))
    except HTTPError as error: raise RuntimeError(f"Gateway HTTP {error.code}") from error
    except URLError as error:
        if isinstance(error.reason,(socket.timeout,TimeoutError)): raise TimeoutError("Gateway request timed out") from error
        raise RuntimeError("Gateway request failed") from error

def save_document(envelope, output_file, overwrite=False):
    if output_file is not None:
        if not isinstance(output_file,str) or not output_file: raise ValueError("outputFile must be a non-empty string")
        if type(overwrite) is not bool: raise ValueError("overwrite must be true or false")
        encoded=find_field(envelope,"contentBase64"); content_value=find_field(envelope,"content")
        if encoded is not None:
            if not isinstance(encoded,str) or len(encoded)>MAX_ENCODED_BYTES: raise RuntimeError("Downloaded document exceeds 20 MiB limit")
            raw=base64.b64decode(encoded,validate=True); source="contentBase64"
        elif isinstance(content_value,str): raw=content_value.encode("utf-8"); source="content"
        elif isinstance(content_value,(dict,list)): raw=(json.dumps(content_value,indent=2,ensure_ascii=False)+"\n").encode("utf-8"); source="content"
        else: raise RuntimeError("Download response did not include writable content")
        if len(raw)>MAX_CONTENT_BYTES: raise RuntimeError("Downloaded document exceeds 20 MiB limit")
        path = Path(output_file).expanduser()
        for ancestor in (path.parent,*path.parent.parents):
            if ancestor.exists() and ancestor.is_symlink(): raise ValueError("outputFile parent directories must not be symlinks")
        path.parent.mkdir(parents=True, exist_ok=True)
        parent_info=path.parent.lstat()
        if path.parent.is_symlink() or not stat.S_ISDIR(parent_info.st_mode): raise ValueError("outputFile parent must be a non-symlink directory")
        if path.exists() or path.is_symlink():
            info=path.lstat()
            if path.is_symlink() or not stat.S_ISREG(info.st_mode): raise ValueError("outputFile must be a regular non-symlink file")
            if not overwrite: raise FileExistsError("outputFile already exists; set overwrite=true to replace it")
        temp_name=None
        try:
            with tempfile.NamedTemporaryFile(mode="wb",delete=False,dir=path.parent,prefix=".amazon-download-") as handle:
                temp_name=handle.name; handle.write(raw); handle.flush(); os.fsync(handle.fileno())
            if overwrite: os.replace(temp_name,path); temp_name=None
            else: os.link(temp_name,path); os.unlink(temp_name); temp_name=None
        finally:
            if temp_name:
                try: os.unlink(temp_name)
                except FileNotFoundError: pass
        envelope={key:value for key,value in envelope.items() if key not in {"contentBase64","content"}}
        envelope.update({"outputFile":str(path),"bytesWritten":len(raw),"writtenFrom":source})
    return envelope

def poll_settings(params):
    timeout=params.get("timeoutSeconds",600); interval=params.get("pollIntervalSeconds",10)
    if isinstance(timeout,bool) or not isinstance(timeout,(int,float)) or not 1<=timeout<=3600: raise ValueError("timeoutSeconds must be a number from 1 to 3600")
    if isinstance(interval,bool) or not isinstance(interval,(int,float)) or not 0.1<=interval<=60: raise ValueError("pollIntervalSeconds must be a number from 0.1 to 60")
    return float(timeout),float(interval)

def wait_or_pending(deadline,interval):
    remaining=deadline-time.monotonic()
    if remaining<=0: return False
    if remaining<=interval:
        time.sleep(remaining); return False
    time.sleep(interval); return True

def pending(resource_key,resource_id,status=None,stage="pending"):
    return {"stage":stage,resource_key:resource_id,"status":status,
            "resume":{"parameter":resource_key,"value":resource_id,"instruction":"Rerun this workflow with the saved identifier."}}

def nonempty_string(value,name):
    if not isinstance(value,str) or not value.strip(): raise ValueError(name+" must be a non-empty string")
    return value

def string_array(value,name):
    if not isinstance(value,list) or not value or any(not isinstance(item,str) or not item.strip() for item in value): raise ValueError(name+" must be a non-empty array of strings")
    return value

def validate_ads_configuration(value):
    if not isinstance(value,dict): raise ValueError("configuration must be an object")
    result=dict(value)
    nonempty_string(result.get("reportTypeId"),"configuration.reportTypeId")
    nonempty_string(result.get("adProduct"),"configuration.adProduct")
    string_array(result.get("groupBy"),"configuration.groupBy")
    string_array(result.get("columns"),"configuration.columns")
    if "timeUnit" in result: nonempty_string(result["timeUnit"],"configuration.timeUnit")
    if "format" in result: nonempty_string(result["format"],"configuration.format")
    filters=result.get("filters")
    if filters is not None:
        if not isinstance(filters,list) or any(not isinstance(item,dict) for item in filters): raise ValueError("configuration.filters must be an array of objects")
        for item in filters:
            nonempty_string(item.get("field"),"configuration.filters.field")
            string_array(item.get("values"),"configuration.filters.values")
    return result

def ads_report(params, common):
    report_id=params.get("reportId")
    if report_id is not None: nonempty_string(report_id,"reportId")
    if not report_id:
        for key in ("startDate","endDate"):
            nonempty_string(params.get(key),key)
        configuration=params.get("configuration")
        if configuration is None:
            for key in ("reportTypeId","adProduct","groupBy","columns"):
                if not params.get(key): raise ValueError(key+" is required when configuration is not supplied")
            configuration={"reportTypeId":params["reportTypeId"],"adProduct":params["adProduct"],"groupBy":params["groupBy"],"columns":params["columns"],"timeUnit":params.get("timeUnit","SUMMARY"),"format":params.get("format","GZIP_JSON")}
            if params.get("filters") is not None: configuration["filters"]=params["filters"]
        configuration=validate_ads_configuration(configuration)
        body={"name":params.get("name") or (str(configuration.get("reportTypeId","report"))+"_"+str(params.get("startDate","resume"))+"_"+str(params.get("endDate","resume"))),"configuration":configuration}
        nonempty_string(body["name"],"name")
        for key in ("startDate","endDate"): body[key]=params[key]
        started=call("/api/skill/amazon/ads/read",{**common,"operation":"ADS_REPORT_START","body":body})
        if not isinstance(started,dict): raise ValueError("Ads report start response must be an object")
        report_id=find_field(started,"reportId")
        nonempty_string(report_id,"started.reportId")
        if started.get("retryable"):
            result=pending("reportId",report_id,stage="pending_duplicate"); result["retryable"]=True; return result
    timeout,interval=poll_settings(params); deadline=time.monotonic()+timeout
    while True:
        if time.monotonic()>=deadline: return pending("reportId",report_id)
        try: state=call("/api/skill/amazon/ads/read",{**common,"operation":"ADS_REPORT_POLL","resourceId":report_id,"body":{}},deadline=deadline)
        except TimeoutError: return pending("reportId",report_id)
        if not isinstance(state,dict): raise ValueError("Ads report poll response must be an object")
        status=find_field(state,"status")
        nonempty_string(status,"state.status")
        if status in {"SUCCESS","COMPLETED"}: break
        if status in {"FAILED","FAILURE","CANCELLED"}: raise RuntimeError("Ads report ended with status "+str(status))
        if not wait_or_pending(deadline,interval): return pending("reportId",report_id,status)
    document_token=find_field(state,"documentToken"); nonempty_string(document_token,"state.documentToken")
    try: downloaded=call("/api/skill/amazon/ads/read",{**common,"operation":"ADS_REPORT_DOWNLOAD","body":{"documentToken":document_token}},deadline=deadline)
    except TimeoutError: return pending("reportId",report_id,status,"pending_document")
    if not isinstance(downloaded,dict): raise ValueError("Ads report download response must be an object")
    return {"reportId":report_id,"status":status,"document":save_document(downloaded,params.get("outputFile"),params.get("overwrite",False))}

def main():
    if len(sys.argv)!=2: raise ValueError("Provide exactly one JSON object argument")
    params=json.loads(sys.argv[1])
    if not isinstance(params,dict): raise ValueError("The argument must be a JSON object")
    if "overwrite" in params and type(params["overwrite"]) is not bool: raise ValueError("overwrite must be true or false")
    if "outputFile" in params and (not isinstance(params["outputFile"],str) or not params["outputFile"]): raise ValueError("outputFile must be a non-empty string")
    common={"connectionId":params["connectionId"]}
    if params.get("workspaceId"): common["workspaceId"]=params["workspaceId"]
    print(json.dumps(ads_report(params,common),indent=2,ensure_ascii=True))

if __name__=="__main__":
    try: main()
    except (KeyError,OSError,ValueError,RuntimeError,json.JSONDecodeError) as error:
        print(json.dumps({"error":str(error)}),file=sys.stderr); raise SystemExit(1)
