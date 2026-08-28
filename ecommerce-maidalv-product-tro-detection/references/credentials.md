# Runtime Configuration and Credentials

Set only the variables required by the selected package-local script. Keep secrets in the environment; never place credentials in CLI arguments, saved payloads, logs, or generated reports.

| Variable | Classification |
|---|---|
| `APP_NAME` | runtime configuration |
| `MODE_ID` | runtime configuration |
| `NEXSCOPE_API_KEY` | secret credential |
| `NEXSCOPE_PROXY_BASE` | runtime configuration |
| `NEXSCOPE_WORKSPACES` | runtime configuration |
| `SESSION_ID` | runtime configuration |

Business and tool-service clients use `NEXSCOPE_PROXY_BASE` with `NEXSCOPE_API_KEY`. Because authorization/account routes are not implemented in that proxy, account workflows use the relevant independently configured `NEXSCOPE_AGENT_*` or `NEXSCOPE_LOGIN_*` base. Third-party connectors use their named provider credentials and endpoints. Missing configuration must fail closed without printing secret values.
