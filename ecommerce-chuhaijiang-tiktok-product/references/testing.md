# Testing ecommerce.chuhaijiang-tiktok-product

## Static and offline gates

- Compile `scripts/chuhaijiang_product_detail.py` with Python.
- Compile `scripts/chuhaijiang_product_image_search.py` with Python.
- Compile `scripts/chuhaijiang_product_rank_most_promoted.py` with Python.
- Compile `scripts/chuhaijiang_product_rank_new_arrivals.py` with Python.
- Compile `scripts/chuhaijiang_product_rank_top_selling.py` with Python.
- Compile `scripts/chuhaijiang_product_related_creators.py` with Python.
- Compile `scripts/chuhaijiang_product_related_lives.py` with Python.
- Compile `scripts/chuhaijiang_product_related_videos.py` with Python.
- Compile `scripts/chuhaijiang_product_reviews.py` with Python.
- Compile `scripts/chuhaijiang_product_search.py` with Python.
- Compile `scripts/upload_image.py` with Python.
- Verify the presign POST uses `/api/v1/tools/research/chuhaijiang/upload/presigned-url` with `NEXSCOPE_API_KEY` Bearer authorization, then PUTs bytes to the returned storage URL without that header.
- Mock a successful Nexscope envelope, an outer nonzero code, HTTP 401, HTTP 402, malformed JSON, and a network timeout.
- Verify the response preserves `X-Cost-Token` and `X-Cost-Credit` as server-reported billing metadata without client-side conversion.
- Verify full responses are stored below `nexscope/<date>/<session>/data` and secrets are never written.
- Verify that no marketplace account or seller credential is requested.

## Live-test status

Not run during staging migration. A paid or credentialed call requires explicit approval. Record timestamp, environment, redacted request, HTTP status, outer code, business status, trace ID, `X-Cost-Token`, calculated credits, `X-Cost-Credit`, and saved response path when testing is approved.
