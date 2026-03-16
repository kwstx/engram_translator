# Engram Testing Guide

This document outlines the procedures for testing the Agent Translator Middleware (Engram) in local and staging environments.

## 1. Environment Setup

### Local Development
1. Clone the repository (if not already done).
2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install development dependencies:
   ```powershell
   pip install -r requirements.txt -r requirements-dev.txt
   ```

### Staging Instance (Docker)
We use a dedicated Docker Compose file for staging to isolate it from production/dev:
```powershell
docker compose -f docker-compose.staging.yml up --build -d
```
This boots up:
- Engram (Staging) on port 8001
- PostgreSQL (Staging)
- Redis (Staging)
- **WireMock** (External Agent Mock) on port 8080
- **Sentry Mock** (Placeholder for error tracking)

## 2. Mocking External Agents (WireMock)

WireMock is pre-configured in the staging environment. 
- Mappings are located in `tests/wiremock/mappings/`.
- Files for responses are in `tests/wiremock/__files/`.

To add a new mock for an external protocol/agent:
1. Create a JSON file in `tests/wiremock/mappings/`.
2. Example mapping:
   ```json
   {
     "request": { "method": "GET", "url": "/agent/capabilities" },
     "response": { "status": 200, "body": "{\"mcp\": true, \"a2a\": true}" }
   }
   ```

## 3. Automated Testing (Pytest)

Run the full suite with coverage:
```powershell
pytest --cov=app tests/
```

### Async Testing
All tests should use `@pytest.mark.asyncio`. Use the `httpx.AsyncClient` for API testing.

### CI/CD Feedback Loop (GitHub Actions)
We run unit tests (excluding `@pytest.mark.integration`) on every pull request, every push to `main`, and on a nightly schedule at **03:00 UTC**. The workflow saves:
- `test-results/pytest.xml` (JUnit report)
- `test-results/pytest.log` (stdout/stderr)
- `coverage.xml` (coverage report)

When a run fails, open the workflow run and download the artifacts to inspect failures locally. Use the log output to prioritize fixes and add/adjust tests that cover the regression.

## 3.1 API Integration Test Examples

These examples are meant for users exploring API integrations and verifying end-to-end behavior.

### Generate a JWT (local)
```powershell
python scripts/generate_token.py --secret $env:AUTH_JWT_SECRET --scope translate:a2a
$env:JWT_TOKEN = "<paste-output-token-here>"
```

### Register an agent
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @{
  agent_id = "beta-agent-a"
  endpoint_url = "http://localhost:8081"
  supported_protocols = @("a2a")
  semantic_tags = @("scheduling")
  is_active = $true
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/register" -Headers $headers -Body $body
```

### Translate a message (requires JWT)
```powershell
$headers = @{
  "Content-Type" = "application/json"
  "Authorization" = "Bearer $env:JWT_TOKEN"
}
$body = @{
  source_agent = "beta-agent-b"
  target_agent = "beta-agent-a"
  payload = @{ intent = "schedule_meeting" }
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/translate" -Headers $headers -Body $body
```

### Curl alternative (cross-platform)
```bash
JWT_TOKEN="<token>"

curl -X POST "http://localhost:8000/api/v1/register" \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"beta-agent-a","endpoint_url":"http://localhost:8081","supported_protocols":["a2a"],"semantic_tags":["scheduling"],"is_active":true}'

curl -X POST "http://localhost:8000/api/v1/translate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer '"$JWT_TOKEN"'" \
  -d '{"source_agent":"beta-agent-b","target_agent":"beta-agent-a","payload":{"intent":"schedule_meeting"}}'
```

## 4. Manual API Checks (Postman)

A Postman collection is recommended for exploratory testing.
- **Base URL**: `http://localhost:8000` (Local) or `http://localhost:8001` (Staging).
- **Authentication**: Include `Authorization: Bearer <test_token>`.
- **Key Endpoints**:
  - `POST /api/v1/translate`: Main protocol conversion.
  - `GET /api/v1/discovery`: Check agent compatibility scores.

## 5. Load Testing (JMeter)

Use JMeter to simulate high traffic between protocol translations.
1. Download [JMeter](https://jmeter.apache.org/download_jmeter.cgi).
2. Create a Thread Group to simulate 100+ concurrent agents.
3. Add an HTTP Request sampler targeting `POST /api/v1/translate` with varied payloads.
4. Monitor "Translation Latency" in Grafana (`http://localhost:3000`).

## 6. Error Tracking (Sentry)

Sentry is integrated in the application. To enable it locally or in staging:
1. Set `SENTRY_DSN` in your `.env` file.
2. In the staging Docker container, it is pre-set to a mock endpoint.
3. Errors are automatically captured and reported with full stack traces and context.

## 7. Test API Keys

For testing, use the following placeholder keys in `.env`:
- `OPENAI_API_KEY`: `sk-test-engram-12345`
- `ANTHROPIC_API_KEY`: `test-anthropic-key`
- `AUTH_JWT_SECRET`: `test-secret-key-do-not-use-in-prod`

## 8. Integration & E2E Testing (New)

We have introduced automated integration flows that simulate end-to-end agent interactions.

### Run Python E2E Suite
This script starts a local server and worker, registers mock agents, and performs a full translation flow with fidelity verification.
```powershell
$env:PYTHONPATH="."
python tests/integration/run_integration_e2e.py
```

### Run PowerShell API Flow (Automation)
A standalone script that uses PowerShell's native REST commands (similar to `curl`) to chain calls.
```powershell
.\scripts\test_api_flow.ps1
```

### Postman Collection
The collection is available at `tests/integration/postman_test_suite.json`. Import this into Postman to manually trigger the integration sequence.

## 9. Input-Output Fidelity Verification
The `run_integration_e2e.py` script includes a comparison engine that:
1. Translates a message from Source Protocol to Target Protocol.
2. Compares the result against a "Gold Standard" expected payload.
3. Outputs a unified diff if translations drift from the expected fidelity.

## 10. Cypress E2E (API Smoke)
We use Cypress for E2E smoke coverage, focused on API flows when a UI is not present.

### Install (one-time)
```powershell
npm install
```

### Run in headless mode
```powershell
npm run cypress:run
```

### Open the interactive runner
```powershell
npm run cypress:open
```

### Environment overrides
```powershell
$env:CYPRESS_BASE_URL="http://localhost:8001"
$env:CYPRESS_AUTH_JWT_SECRET="local-test-secret"
$env:CYPRESS_AUTH_ISSUER="https://auth.example.com/"
$env:CYPRESS_AUTH_AUDIENCE="translator-middleware"
```

Tests live in `cypress/e2e/` and currently validate:
- `/metrics` is reachable
- A2A → MCP success via `POST /api/v1/beta/translate`
- A2A → ACP returns `422` when no route exists

## 11. User Acceptance Testing (UAT) with Beta Users

Use a short, consistent beta cycle to gather integration feedback before releases:

1. Create a beta test plan
   - Target APIs: `POST /api/v1/register`, `GET /api/v1/discovery/collaborators`, `POST /api/v1/translate`
   - Supported protocols: A2A, MCP, ACP
   - Success criteria: end-to-end translation with no manual field edits
2. Provide beta testers with:
   - Base URL and JWT token
   - The API examples above
   - A short checklist of scenarios to run (single hop, multi hop, error handling)
3. Collect feedback from:
   - CI artifacts (`pytest.log`, `pytest.xml`)
   - App logs (translation failures and mapping suggestions)
   - A shared feedback template (issue, steps, expected, actual, logs)
4. Iterate on fixes:
   - Add or update tests for each defect
   - Re-run CI and confirm artifact logs are clean
