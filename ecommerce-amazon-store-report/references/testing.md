# Verification guide

1. Run `python scripts/amazon_sp_api.py --list` and confirm the operation count is 4.
2. Save the illustrative request for `amazon-sp-api-reports-getreport` from `api.json` as `request.json`. Run `python scripts/amazon_sp_api.py amazon-sp-api-reports-getreport --input request.json` and check that it reports the public endpoint without sending a request.
3. Confirm that missing required fields, a wrong connection ID type and an unknown operation fail locally. A write confirmation or disconnect also needs `--confirm-write`.
4. In TEST, replace fictional inputs with an owned connection and appropriate identifiers. Run the chosen operation only with approval. Inspect the Nexscope and Amazon statuses, and confirm that no credentials are included in the verification notes.

Create and poll reports as separate requests. Resume using the returned report ID. Document metadata and download URLs are private.

Treat this guide and its sample values as local verification material. A successful preview does not establish a successful write.
