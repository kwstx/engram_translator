# Agent Translator Middleware

Security notes:
- JWT authentication is required for `/api/v1/translate` with scope `translate:a2a`.
- Tokens must be issued by your auth service and validated via `AUTH_ISSUER` and `AUTH_AUDIENCE`.
- Rate limiting is enabled globally at 100 requests per minute per IP.
- In production, terminate TLS with Let's Encrypt and enable HTTPS redirect (`HTTPS_ONLY=true`).

Environment variables:
- `AUTH_ISSUER` (default: `https://auth.example.com/`)
- `AUTH_AUDIENCE` (default: `translator-middleware`)
- `AUTH_JWT_ALGORITHM` (default: `HS256`)
- `AUTH_JWT_SECRET` (required for HS* algorithms)
- `AUTH_JWT_PUBLIC_KEY` (required for RS*/ES* algorithms)
- `HTTPS_ONLY` (default: `false`)
- `TASK_POLL_INTERVAL_SECONDS` (default: `2`)
- `TASK_LEASE_SECONDS` (default: `60`)
- `TASK_MAX_ATTEMPTS` (default: `5`)
- `AGENT_MESSAGE_LEASE_SECONDS` (default: `60`)
- `AGENT_MESSAGE_MAX_ATTEMPTS` (default: `5`)

Queue API:
- `POST /api/v1/queue/enqueue` enqueues a translation task.
- `POST /api/v1/agents/{agent_id}/messages/poll` leases the next message for an agent.
- `POST /api/v1/agents/messages/{message_id}/ack` acknowledges a leased message.
