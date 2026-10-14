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
| imageBase64 | Exactly one image source; pure Base64, 16–12582912 encoded characters, no data URI prefix |
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

Both routes use the Nexscope platform envelope. Example complete response, with illustrative candidate values:

```json
{"code":0,"msg":null,"data":{"data":{"code":"OK","request_id":"example-request","data":{"candidates":[{"design_registration_id":"example-design-id","title_en":"Bottle","similarity":85.97,"holder_names":["Example holder"],"simple_legal_status":"inactive","locarno_classes":["09-01"],"image_available":true}],"coverage":{"metadata_unknown":{"legal_status":1}},"warnings":["metadata_incomplete"]}}},"traceId":"example-trace"}
```

The source envelope is retained: platform `data.data.code` must be `OK`, and `data.data.data.candidates` is the actual list. Preserve all returned metadata. Candidates may include registration/application/publication numbers, jurisdiction codes, titles, holder/designer names, Locarno classes, dates, raw image/text scores, similarity, status and source risk hints. Missing values remain unknown. Preserve warnings and coverage; `coverage_ratio` can exceed 1. Never fabricate image URLs from `image_available`.

HTTP 401: Nexscope authentication failure. HTTP 402: insufficient credits. Field errors: correct the documented input; do not retry automatically. Source/configuration failures are backend matters. HTTP 200 with nonzero platform code, non-OK source status or malformed candidates is a failure, not a zero-match result. Failed requests are never cached. Cache hits do not verify current key validity online and do not create a new charge.
