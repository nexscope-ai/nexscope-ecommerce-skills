# Verification guide

1. Run `python scripts/amazon_sp_api.py --list` and confirm the operation count is 10.
2. Save the illustrative request for `amazon-sp-api-orders-getorder-3` from `api.json` as `request.json`. Run `python scripts/amazon_sp_api.py amazon-sp-api-orders-getorder-3 --input request.json` and check that it reports the public endpoint without sending a request.
3. Confirm that missing required fields, a wrong connection ID type and an unknown operation fail locally. A write confirmation or disconnect also needs `--confirm-write`.
4. In TEST, replace fictional inputs with an owned connection and appropriate identifiers. Run the chosen operation only with approval. Inspect the Nexscope and Amazon statuses, and confirm that no credentials are included in the verification notes.

Use the selected marketplace and order identifier. Restrict order and buyer data to the requesting user and avoid showing unnecessary personal fields.

Treat this guide and its sample values as local verification material. A successful preview does not establish a successful write.
