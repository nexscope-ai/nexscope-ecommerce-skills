# Design Similarity Search API

The bundled client uses the existing research compatibility route. The public business address, short address and MCP identity below require the corresponding backend catalog release; their presence in this package does not confirm deployment in your environment. The compatibility route was verified in the Nexscope test environment on 2026-10-14.

- Public business API: `POST ${NEXSCOPE_PROXY_BASE}/api/skill-api/v1/skills/design-similarity-search/run`
- Short business address (same executor): `POST ${NEXSCOPE_PROXY_BASE}/ai/designSimilaritySearch`
- Compatible research route used by the client: `POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ecDw/designSimilarSearch`
- MCP tool: `nexscope_design_similarity_search`; use the same JSON parameters.
- Authentication: `Authorization: Bearer ${NEXSCOPE_API_KEY}`. Base defaults to `https://api.nexscope.ai`.
- Calls consume credits through the existing Nexscope billing chain. `cost` is elapsed milliseconds, not credits. Do not assume a fixed price from upstream usage or topK.

| Field | Contract |
|---|---|
| imageUrl | Exactly one image source; public HTTP(S) URL, 8–4096 characters, no embedded credentials |
| imageBase64 | Exactly one image source; pure Base64, 16–20971520 encoded characters, no data URI prefix |
| title | Optional trimmed string, 1–4096 characters; context for image, not text-only retrieval |
| topK | Optional integer, default 20, range 1–200 |
| regions | Optional distinct two-letter strings, max 64; e.g. US, EM; EU source is represented as EM here |
| jurisdictionCodes | Optional distinct source-code strings, 2–8 letters, max 32; e.g. USID/EMID; intersects regions |
| topLoc | Optional distinct two-digit strings, max 32; e.g. ["09"] |
| locarnoClasses | Optional distinct NN-NN strings, max 64; e.g. ["09-01"] |
| patentStatus | Optional distinct integer array [0], [1] or [0,1]; 0 inactive, 1 active; omit for no preference |

Omit unused fields; null/scalar filter values, duplicate items, numeric strings, unknown fields and both/no image sources are rejected. Classification strings preserve leading zeros. The client validates before network access.

Example request (replace image URL with the user's actual reachable image):

```json
{"imageUrl":"https://example.com/product.png","title":"Bottle","topK":20,"regions":["US","EM"],"topLoc":["09"]}
```

Prepare local image input without upload:

```bash
python -c "import base64,json; from pathlib import Path; Path('request.json').write_text(json.dumps({'imageBase64':base64.b64encode(Path('product.png').read_bytes()).decode('ascii'),'topK':20}),encoding='utf-8')"
python scripts/design_similarity.py --params-file request.json
# After approval: add --execute. --no-cache refreshes deliberately.
```

Both routes use the Nexscope platform envelope. Illustrative response (not a paid-call or pricing calibration):

```json
{
  "code": 0,
  "data": {
    "data": {
      "code": "OK",
      "message": "success",
      "request_id": "req_example",
      "data": {
        "total": 1,
        "candidates": [
          {
            "design_registration_id": "DSR:euipo_design:001694860-0001",
            "registration_jurisdiction_code": "EU",
            "jurisdiction_iso2": "EM",
            "primary_identifier": "001694860-0001",
            "application_number": "001694860",
            "registration_number": "E077151-PC",
            "publication_number": null,
            "title": "E077151-PC",
            "title_language": "unknown",
            "title_en": "Chairs [seats]",
            "designer_names": null,
            "locarno_classes": [
              "06.01"
            ],
            "holder_names": [
              "237302"
            ],
            "simple_legal_status": "inactive",
            "application_date": "2010-04-13",
            "registration_date": null,
            "publication_date": null,
            "similarity": 99.88,
            "risk_level": "medium",
            "image_url": "https://example.com/design-1.png?signature=example%2Bsignature&expires=2000000000",
            "images": [
              "https://example.com/design-1.png?signature=example%2Bsignature&expires=2000000000",
              "https://example.com/design-2.png?signature=second&expires=2000000000"
            ],
            "specification": null,
            "novelty_statement": null,
            "applicant_addresses": null,
            "locarno_details": [
              {
                "code": "06.01",
                "parent_code": "06",
                "label_zh": null,
                "label_en": null
              }
            ],
            "estimated_expiration_date": null,
            "expiration_date_basis": null,
            "tro_cases": [],
            "protected_jurisdictions": [
              "EM"
            ]
          }
        ]
      }
    }
  }
}
```

In the complete Nexscope response, require numeric platform `code:0`, source `data.data.code:OK`, no failure marker and a list at `data.data.data.candidates`. In the retained source/gateway envelope alone the list is `data.data.candidates`; do not drop an envelope layer when reading the complete platform response. `data.data.data.total` counts returned candidates, not the corpus or billing units. Source `data.usage` (complete platform `data.data.usage`) is provider-account usage, never user debit or balance. Preserve gateway/service `requestId`, upstream `data.request_id` and extracted `upstreamRequestId` separately wherever returned; keep the platform `traceId` as well. Actual Nexscope fee headers take precedence; missing fees do not mean free.

### Search candidate fields — source contract 2026-10-31

All 29 business fields below can be absent or null; that means unknown. Dates are YYYY-MM-DD. Preserve every returned field and the original candidate order. Similarity is the final 0–100 score: do not multiply by 100, combine scores, sort again or call it an infringement probability. Complete signed image URLs and image order are retained; with images, `image_url == images[0]`. Empty TRO associations are not confirmation of no TRO; an estimated expiration date is not confirmed invalidity.

| Field | Type | Meaning |
|---|---|---|
| `design_registration_id` | string | Exact registration ID for details; preserve unchanged. |
| `registration_jurisdiction_code` | string | Source jurisdiction code such as EU, EMID or USID; do not rewrite as ISO-2. |
| `jurisdiction_iso2` | string | Registration jurisdiction, distinct from protected jurisdictions. |
| `primary_identifier` | string | Primary display number; retain leading zeros. |
| `application_number` | string | Source application number. |
| `registration_number` | string | Source registration number. |
| `publication_number` | string | Source publication number; missing or null means unknown. |
| `title` | string | Source title, which may be a number. |
| `title_language` | string | Source title language; may be unknown. |
| `title_en` | string | Source English title; do not translate missing values. |
| `designer_names` | array | Source designers; missing or null means unknown. |
| `locarno_classes` | array | Preserve output codes such as 06.01 or 09-01; requests still require NN-NN. |
| `holder_names` | array | Source holders; do not resolve numeric identifiers to invented names. |
| `simple_legal_status` | string | Source legal status; do not infer it from similarity. |
| `application_date` | string | Source application date, YYYY-MM-DD. |
| `registration_date` | string | Source registration date, YYYY-MM-DD. |
| `publication_date` | string | Source publication date, YYYY-MM-DD. |
| `similarity` | number | Final 0-100 score, not a probability. Preserve returned order; never multiply by 100 or sort again. |
| `risk_level` | string | Source risk hint, separate from score and legal status; not an infringement verdict. |
| `image_url` | string | Complete signed first-image URL; when images exist this equals images[0]. Never strip query parameters. |
| `images` | array | At most six complete signed image URLs in original order; empty means no available images. |
| `specification` | JSON/null | Source JSON of any shape, or null; preserve actual structure without filling gaps. |
| `novelty_statement` | string | Source novelty statement; retain original text, not a legal conclusion. |
| `applicant_addresses` | array | Source applicant objects with name and address; never infer protection jurisdictions. |
| `locarno_details` | array | Source code, parent_code, label_zh and label_en; missing labels stay unknown. |
| `estimated_expiration_date` | string | Estimated date only, YYYY-MM-DD; not confirmed expiry or invalidity. |
| `expiration_date_basis` | JSON/null | Source JSON of any shape, or null; never invent an estimation basis. |
| `tro_cases` | array | Current TRO corpus associations; empty is not confirmation of no TRO. |
| `protected_jurisdictions` | array | HAGUE designated states or ordinary registration jurisdiction; null means unknown, never fill from regions. |

`locarno_details[]` contains source `code`, `parent_code`, and nullable `label_zh`/`label_en`; never invent missing labels. `applicant_addresses[]` may contain `name` and `address`; an address does not establish protected jurisdiction. `specification` and `expiration_date_basis` retain arbitrary returned JSON. Output `06.01` or `09-01` does not relax request `locarnoClasses` NN-NN validation. All five filter arrays reject null arrays/elements and duplicates; unused filters should be omitted. Preserve optional coverage, warnings and execution diagnostics when returned without assuming the earlier diagnostic structure is always present.

| Source error | Handling |
|---|---|
| 400 / DATA_IMAGE_DOWNLOAD_FAILED | Preserve code and request identifiers; check the supplied image, no automatic replacement or Base64 retry. |
| 413 / SYSTEM_PAYLOAD_TOO_LARGE | Whole request exceeds source limit; no automatic compression or retry. The Base64 field limit remains 20971520 characters. |
| 502 / SR_QUERY_ERROR | Source query failed; not zero candidates or insufficient user credits. |
| 503 / CAPABILITY_BACKEND_UNAVAILABLE | Source capability unavailable; not zero candidates or a top-up prompt. |
| 401 / 402 / 403 | Authentication / insufficient Nexscope credits / permission failure respectively; stop and preserve the actual error. |
| non-OK source code, error marker, 5xx or timeout | Failed or uncertain request; never cache as success or retry automatically. |

Cache hits do not verify current key validity online and do not create a new charge. Retain the response and diagnostics without converting source usage to user pricing.


## Design Registration Details

- Public API: `POST ${NEXSCOPE_PROXY_BASE}/api/skill-api/v1/skills/design-registration-details/run`
- Short address: `POST ${NEXSCOPE_PROXY_BASE}/ai/designRegistrationDetails`
- Client research route: `POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ecDw/designProfile`
- MCP: `nexscope_design_registration_details`

These new addresses require the corresponding backend deployment. No live deployment or credit calibration is established by this package update.

| Field | Contract |
|---|---|
| designRegistrationIds | Exactly one identifier mode; 1–200 unique strings, each 1–128 characters without leading/trailing whitespace; excludes jurisdictionIso2 |
| primaryIdentifier | Exactly one identifier mode; 1–128 character string without leading/trailing whitespace; preserve leading zeros |
| jurisdictionIso2 | Optional only with primaryIdentifier; exactly two English letters, e.g. US or EM |

Example request: `{"primaryIdentifier":"001431738","jurisdictionIso2":"EM"}`. Registration IDs must be supplied by the user or returned by search, never synthesized from publication/registration numbers. No automatic batching or resubmission.

Illustrative response (fees deliberately omitted; not live calibration):

```json
{"code":0,"data":{"data":{"code":"OK","request_id":"example-request","data":{"returned":1,"items":[{"design_registration_id":"DSR:wipo_hague:EMID.001431738-0001","primary_identifier":"001431738","holder_names":["Example holder"],"designer_names":["Example designer"],"simple_legal_status":"inactive","as_of_date":"2026-10-09","locarno_classes":["09-01"],"has_readable_image":1,"image_count":5}],"execution":{"engine":"starrocks","elapsed_ms":27,"row_count":1}}}}}
```

Require platform numeric code 0, source data.data.code OK, no error field and a list at data.data.data.items. Details use items, never candidates. Preserve all matches and original order. returned is the response count, not dataset size. Optional asset/asset_code and execution identify source assets/execution; source usage is not user billing. A not-found result or source failure is not zero matches or an infringement verdict.

Item metadata may include design_registration_id, primary_identifier, application_number, registration_number, publication_number, as_of_date, data_version, right_type, registration_jurisdiction, registration_jurisdiction_code, jurisdiction_iso2, title, title_language, title_en, title_en_source, simple_legal_status, raw_status, application_date, registration_date, publication_date, locarno_classes, holder_names, designer_names, classification_count, party_count, has_readable_image, image_count, text_count, data_quality_level and coverage_level. Missing/null values are unknown; do not infer missing parties or today's status. Preserve date strings and source language/status values.

Details return no image URL. has_readable_image is an integer and image_count counts source image facts; neither permits constructing URLs. Search candidates may have optional/null image_url: use only its returned value unchanged. HTTP 401 means Nexscope authentication failed; 402 means insufficient credits. Stop on authorization, source, HTTP or malformed-response errors without automatic region/store substitution, retries or lookup-mode changes. Both operations consume credits; source fee examples do not establish Nexscope pricing.

Detail request limits are unchanged by the 2026-10-31 source update. Preserve requestId separately from upstream request_id/upstreamRequestId and platform traceId. DATA_DESIGN_NOT_FOUND is not proof that no rights exist; no automatic lookup-mode changes or generated image URLs.

## API Key request rate and retries

All API Keys of one Nexscope user share the public API execution request-rate allowance, measured in any rolling 1-second window. The allowed RPS depends on that user's entitlements; it is not a universal 1 RPS. One Skill operation may issue multiple public API requests, each of which uses the allowance.

HTTP 429 with Nexscope outer code `13012` means request-rate exhaustion: honor the response's `Retry-After`. Outer code `13013` means concurrent-request exhaustion, not rate exhaustion; honor `Retry-After` when supplied. Check the HTTP status and outer JSON code separately. Do not automatically replay writes or requests with uncertain outcomes; first reconcile the operation's state.
