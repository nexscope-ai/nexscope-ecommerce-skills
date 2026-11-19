# Amazon Customer Feedback API reference

Migration reference: `linkfox-amazon-store-customer-feedback` from the reviewed supplier master.

These operations use Nexscope public Data API endpoints below. The legacy `/api/v1/tools/research/` routes do not implement this contract.
Use `NEXSCOPE_API_KEY` and optionally `NEXSCOPE_PROXY_BASE`. All request and response JSON in `api.json` is illustrative.

| Operation | Nexscope POST path | Scope |
| --- | --- | --- |
| `getbrowsenodereturntopics` | `/spapi/getBrowseNodeReturnTopics` | Authorized connection where required |
| `getbrowsenodereturntrends` | `/spapi/getBrowseNodeReturnTrends` | Authorized connection where required |
| `getbrowsenodereviewtopics` | `/spapi/getBrowseNodeReviewTopics` | Authorized connection where required |
| `getbrowsenodereviewtrends` | `/spapi/getBrowseNodeReviewTrends` | Authorized connection where required |
| `getitembrowsenode` | `/spapi/getItemBrowseNode` | Authorized connection where required |
| `getitemreviewtopics` | `/spapi/getItemReviewTopics` | Authorized connection where required |
| `getitemreviewtrends` | `/spapi/getItemReviewTrends` | Authorized connection where required |

## Parameters and examples

See the field definitions and JSON examples below, or use the machine-readable `api.json`.

### `amazon-sp-api-customer-feedback-getbrowsenodereturntopics`

MCP tool: `nexscope_amazon_sp_api_customer_feedback_getbrowsen_db94aca4457a`.

Amazon operation: `GET /customerFeedback/2024-06-01/browseNodes/{browseNodeId}/returns/topics`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: browseNodeId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "browseNodeId": "123456"
  },
  "queryString": "marketplaceId=ATVPDKIKX0DER"
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "sellerId": "EXAMPLE_SELLER",
    "requestId": "example-request-id",
    "source": "BACKEND_AMAZON_SP_API",
    "response": {
      "httpStatus": 200,
      "payload": {
        "browseNodeId": "123456",
        "displayName": "EXAMPLE",
        "marketplaceId": "ATVPDKIKX0DER",
        "countryCode": "US",
        "dateRange": {
          "startDate": "2026-01-01T00:00:00Z",
          "endDate": "2026-01-02T00:00:00Z"
        },
        "topics": [
          {
            "topic": "EXAMPLE",
            "browseNodeMetrics": {
              "occurrencePercentage": {
                "allProducts": 1
              }
            }
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-customer-feedback-getbrowsenodereturntrends`

MCP tool: `nexscope_amazon_sp_api_customer_feedback_getbrowsen_300091668754`.

Amazon operation: `GET /customerFeedback/2024-06-01/browseNodes/{browseNodeId}/returns/trends`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: browseNodeId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "browseNodeId": "123456"
  },
  "queryString": "marketplaceId=ATVPDKIKX0DER"
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "sellerId": "EXAMPLE_SELLER",
    "requestId": "example-request-id",
    "source": "BACKEND_AMAZON_SP_API",
    "response": {
      "httpStatus": 200,
      "payload": {
        "browseNodeId": "123456",
        "displayName": "EXAMPLE",
        "marketplaceId": "ATVPDKIKX0DER",
        "countryCode": "US",
        "dateRange": {
          "startDate": "2026-01-01T00:00:00Z",
          "endDate": "2026-01-02T00:00:00Z"
        },
        "returnTrends": [
          {
            "topic": "EXAMPLE",
            "trendMetrics": [
              {
                "dateRange": {
                  "startDate": "2026-01-01T00:00:00Z",
                  "endDate": "2026-01-02T00:00:00Z"
                },
                "browseNodeMetrics": {
                  "occurrencePercentage": {
                    "allProducts": 1
                  }
                }
              }
            ]
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-customer-feedback-getbrowsenodereviewtopics`

MCP tool: `nexscope_amazon_sp_api_customer_feedback_getbrowsen_b326f4966468`.

Amazon operation: `GET /customerFeedback/2024-06-01/browseNodes/{browseNodeId}/reviews/topics`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: browseNodeId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "browseNodeId": "123456"
  },
  "queryString": "marketplaceId=ATVPDKIKX0DER&sortBy=MENTIONS"
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "sellerId": "EXAMPLE_SELLER",
    "requestId": "example-request-id",
    "source": "BACKEND_AMAZON_SP_API",
    "response": {
      "httpStatus": 200,
      "payload": {
        "browseNodeId": "123456",
        "displayName": "EXAMPLE",
        "marketplaceId": "ATVPDKIKX0DER",
        "countryCode": "US",
        "dateRange": {
          "startDate": "2026-01-01T00:00:00Z",
          "endDate": "2026-01-02T00:00:00Z"
        },
        "topics": {
          "positiveTopics": [
            {
              "topic": "EXAMPLE",
              "browseNodeMetrics": {}
            }
          ],
          "negativeTopics": [
            {
              "topic": "EXAMPLE",
              "browseNodeMetrics": {}
            }
          ]
        }
      }
    }
  }
}
```

### `amazon-sp-api-customer-feedback-getbrowsenodereviewtrends`

MCP tool: `nexscope_amazon_sp_api_customer_feedback_getbrowsen_09da7f5d2027`.

Amazon operation: `GET /customerFeedback/2024-06-01/browseNodes/{browseNodeId}/reviews/trends`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: browseNodeId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "browseNodeId": "123456"
  },
  "queryString": "marketplaceId=ATVPDKIKX0DER"
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "sellerId": "EXAMPLE_SELLER",
    "requestId": "example-request-id",
    "source": "BACKEND_AMAZON_SP_API",
    "response": {
      "httpStatus": 200,
      "payload": {
        "browseNodeId": "123456",
        "displayName": "EXAMPLE",
        "marketplaceId": "ATVPDKIKX0DER",
        "countryCode": "US",
        "dateRange": {
          "startDate": "2026-01-01T00:00:00Z",
          "endDate": "2026-01-02T00:00:00Z"
        },
        "reviewTrends": {
          "positiveTopics": [
            {
              "topic": "EXAMPLE",
              "trendMetrics": [
                {
                  "dateRange": {
                    "startDate": "2026-01-01T00:00:00Z",
                    "endDate": "2026-01-02T00:00:00Z"
                  },
                  "browseNodeMetrics": {
                    "occurrencePercentage": {
                      "topTwentyFivePercentProducts": 1,
                      "allProducts": 1
                    }
                  }
                }
              ]
            }
          ],
          "negativeTopics": [
            {
              "topic": "EXAMPLE",
              "trendMetrics": [
                {
                  "dateRange": {
                    "startDate": "2026-01-01T00:00:00Z",
                    "endDate": "2026-01-02T00:00:00Z"
                  },
                  "browseNodeMetrics": {
                    "occurrencePercentage": {
                      "topTwentyFivePercentProducts": 1,
                      "allProducts": 1
                    }
                  }
                }
              ]
            }
          ]
        }
      }
    }
  }
}
```

### `amazon-sp-api-customer-feedback-getitembrowsenode`

MCP tool: `nexscope_amazon_sp_api_customer_feedback_getitembrowsenode`.

Amazon operation: `GET /customerFeedback/2024-06-01/items/{asin}/browseNode`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: asin.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "asin": "B000EXAMPL"
  },
  "queryString": "marketplaceId=ATVPDKIKX0DER"
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "sellerId": "EXAMPLE_SELLER",
    "requestId": "example-request-id",
    "source": "BACKEND_AMAZON_SP_API",
    "response": {
      "httpStatus": 200,
      "payload": {
        "browseNodeId": "123456",
        "displayName": "EXAMPLE"
      }
    }
  }
}
```

### `amazon-sp-api-customer-feedback-getitemreviewtopics`

MCP tool: `nexscope_amazon_sp_api_customer_feedback_getitemreviewtopics`.

Amazon operation: `GET /customerFeedback/2024-06-01/items/{asin}/reviews/topics`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: asin.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "asin": "B000EXAMPL"
  },
  "queryString": "marketplaceId=ATVPDKIKX0DER&sortBy=MENTIONS"
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "sellerId": "EXAMPLE_SELLER",
    "requestId": "example-request-id",
    "source": "BACKEND_AMAZON_SP_API",
    "response": {
      "httpStatus": 200,
      "payload": {
        "asin": "B000EXAMPL",
        "itemName": "EXAMPLE",
        "marketplaceId": "ATVPDKIKX0DER",
        "countryCode": "US",
        "dateRange": {
          "startDate": "2026-01-01T00:00:00Z",
          "endDate": "2026-01-02T00:00:00Z"
        },
        "topics": {
          "positiveTopics": [
            {
              "topic": "EXAMPLE",
              "asinMetrics": {}
            }
          ],
          "negativeTopics": [
            {
              "topic": "EXAMPLE",
              "asinMetrics": {}
            }
          ]
        }
      }
    }
  }
}
```

### `amazon-sp-api-customer-feedback-getitemreviewtrends`

MCP tool: `nexscope_amazon_sp_api_customer_feedback_getitemreviewtrends`.

Amazon operation: `GET /customerFeedback/2024-06-01/items/{asin}/reviews/trends`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: asin.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "asin": "B000EXAMPL"
  },
  "queryString": "marketplaceId=ATVPDKIKX0DER"
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "sellerId": "EXAMPLE_SELLER",
    "requestId": "example-request-id",
    "source": "BACKEND_AMAZON_SP_API",
    "response": {
      "httpStatus": 200,
      "payload": {
        "asin": "B000EXAMPL",
        "itemName": "EXAMPLE",
        "marketplaceId": "ATVPDKIKX0DER",
        "countryCode": "US",
        "dateRange": {
          "startDate": "2026-01-01T00:00:00Z",
          "endDate": "2026-01-02T00:00:00Z"
        },
        "reviewTrends": {
          "positiveTopics": [
            {
              "topic": "EXAMPLE",
              "trendMetrics": [
                {
                  "dateRange": {
                    "startDate": "2026-01-01T00:00:00Z",
                    "endDate": "2026-01-02T00:00:00Z"
                  },
                  "asinMetrics": {
                    "occurrencePercentage": 1
                  }
                }
              ]
            }
          ],
          "negativeTopics": [
            {
              "topic": "EXAMPLE",
              "trendMetrics": [
                {
                  "dateRange": {
                    "startDate": "2026-01-01T00:00:00Z",
                    "endDate": "2026-01-02T00:00:00Z"
                  },
                  "asinMetrics": {
                    "occurrencePercentage": 1
                  }
                }
              ]
            }
          ]
        }
      }
    }
  }
}
```
