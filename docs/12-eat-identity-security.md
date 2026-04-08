# EAT Identity & Security

Engram uses a unified token system called **EAT** (Engram Authorization Token) that carries both structured permissions per tool and semantic scopes derived from the OWL ontology. This page covers authentication, authorization, token lifecycle, credential storage, and the security middleware stack.

---

## What is EAT?

An EAT is a JWT-based token that carries three types of authorization data:

1. **Identity** (`sub` claim) — Who you are (email or user ID)
2. **Structured Permissions** (`scopes` claim) — Per-tool permissions as a nested object
3. **Semantic Scopes** (`semantic_scopes` claim) — Ontology-derived capabilities from `security.owl`

### Token Structure

```json
{
  "sub": "user@company.com",
  "jti": "unique-token-id",
  "exp": 1712345678,
  "scopes": {
    "slack": ["send_message", "list_channels"],
    "docker": ["run", "ps", "images"]
  },
  "semantic_scopes": [
    "execute:tool-invocation",
    "read:ontology-metadata"
  ]
}
```

| Claim | Type | Description |
|---|---|---|
| `sub` | `str` | User identity (email or UUID) |
| `jti` | `str` | Unique token ID for revocation tracking |
| `exp` | `int` | Expiration timestamp (Unix epoch) |
| `scopes` | `dict` | Per-tool permissions: `{"tool_name": ["action1", "action2"]}` |
| `semantic_scopes` | `list` | Ontology-based capabilities: `["execute:tool-invocation"]` |

---

## Authentication Flow

### Step 1: Sign Up or Log In

```bash
# Via CLI
engram auth login

# Via TUI
engram run --debug   # Uses inline login form
```

The flow:
1. **Signup** — `POST /auth/signup` with email and password → Creates user record
2. **Login** — `POST /auth/login` with email and password → Returns a session `access_token`
3. **EAT Generation** — `POST /auth/tokens/generate-eat` with the session token → Returns the EAT

### Step 2: Token Storage

EAT tokens are stored securely using a priority chain:

| Priority | Method | Where | Security |
|---|---|---|---|
| 1 | System keyring | OS credential store | Highest (OS-managed encryption) |
| 2 | Config fallback | `~/.engram/config.yaml` | Medium (file permissions) |
| 3 | TUI encrypted | `~/.engram/config.enc` | High (Fernet symmetric encryption) |

The CLI uses the `keyring` library to store tokens in:
- **macOS** — Keychain
- **Windows** — Credential Locker
- **Linux** — Secret Service (GNOME Keyring / KWallet)

If the system keyring is unavailable, tokens fall back to the `config.yaml` file.

---

## Token Lifecycle

### EATIdentityService

The `EATIdentityService` (`app/services/eat_identity.py`) manages the full token lifecycle:

### Issue

```python
result = EATIdentityService.issue_token(
    db=session,
    user_id="user-uuid",
    permissions={"slack": ["send_message"]},
    semantic_scopes=["execute:tool-invocation"],
)
# Returns: EATIssueResult(token=..., refresh_token=..., expires_at=..., jti=...)
```

### Refresh

```python
result = EATIdentityService.refresh_token(
    db=session,
    refresh_token="refresh-uuid",
    permissions={"slack": ["send_message"]},
)
```

Refresh tokens are:
- Stored in Redis with the hash of the token as the key
- Single-use (consumed on refresh, a new refresh token is issued)
- Expire in `EAT_REFRESH_TOKEN_EXPIRE_MINUTES` (default: 7 days)

### Revoke

```python
EATIdentityService.revoke_eat(
    db=session,
    user_id="user-uuid",
    token="eat-jwt",
    jti="token-jti",
    expires_in=900,
    refresh_token="refresh-uuid",
)
```

Revocation:
1. Adds the JTI to the Redis deny list (checked on every request)
2. Deletes the refresh token from Redis
3. Creates an audit log entry with event type `REVOKED`

### Token Expiration

| Token Type | Default Lifetime | Configuration |
|---|---|---|
| **Session token** | 7 days | `ACCESS_TOKEN_EXPIRE_MINUTES` |
| **EAT access token** | 15 minutes | `EAT_ACCESS_TOKEN_EXPIRE_MINUTES` |
| **EAT refresh token** | 7 days | `EAT_REFRESH_TOKEN_EXPIRE_MINUTES` |

The EAT access token is intentionally short-lived (15 minutes by default) because it carries permissions. The refresh token allows silent renewal without re-authentication.

---

## Semantic Scopes

Semantic scopes are derived from `security.owl` and provide ontology-backed access control:

| Scope | Ontology Context | Capability |
|---|---|---|
| `execute:tool-invocation` | Global | Can invoke cross-protocol tool translations |
| `read:ontology-metadata` | Global | Can query ontology metadata and tool catalogs |
| `write:tool-registry` | Global | Can register and modify tools |
| `admin:system` | Global | Full administrative access |

### Fail-Closed Semantics

| Setting | Default | Behavior |
|---|---|---|
| `AUTH_FAIL_CLOSED` | `true` | When Redis is down and the JTI deny list can't be checked, **deny access** |
| `SEMANTIC_AUTH_FAIL_CLOSED` | `true` | When semantic scope verification fails, **deny access** |

This fail-closed design ensures that security checks never silently pass due to infrastructure failures.

### Viewing Scopes

```bash
# Full identity tree with scopes
engram auth whoami

# Tabular scope view with ontology context
engram auth scope
```

---

## Token Audit Trail

Every token event is logged in the `TokenAuditLog` database table:

| Event Type | When |
|---|---|
| `ISSUED` | New EAT is generated |
| `REFRESHED` | EAT is renewed via refresh token |
| `REVOKED` | EAT is explicitly revoked |

Each audit record captures:
- User ID, token type, JTI
- Token hash (SHA-256, not the actual token)
- Issued and expiration timestamps
- Current scopes and semantic scopes
- Additional metadata

---

## Credential Storage

Provider credentials (API keys for Claude, Slack, Perplexity, etc.) are stored separately from EAT tokens:

### CredentialService

The `CredentialService` (`app/services/credentials.py`) encrypts and manages provider credentials:

```python
await CredentialService.save_credential(
    db=session,
    user_id=user_uuid,
    provider_name="claude",
    token="sk-ant-...",
    credential_type=CredentialType.API_KEY,
)
```

| Feature | Detail |
|---|---|
| **Encryption** | Fernet symmetric encryption via `CryptoService` |
| **Encryption key** | `PROVIDER_CREDENTIALS_ENCRYPTION_KEY` environment variable |
| **Auto-refresh** | OAuth tokens are automatically refreshed on expiration |
| **Per-user isolation** | Each user has their own credential set |

### Supported Auth Types

| Type | Examples | Storage |
|---|---|---|
| `api_key` | Anthropic, OpenAI, Perplexity | Encrypted API key |
| `oauth` | Slack, Google | Encrypted access + refresh tokens |

### TUI Vault Service

The TUI uses a separate vault (`tui/vault_service.py`) for credential storage, backed by Fernet-encrypted files at `~/.engram/config.enc`. This is designed for environments where the system keyring isn't available.

---

## Security Headers

The following security headers are injected on every response:

| Header | Value | Purpose |
|---|---|---|
| `X-Content-Type-Options` | `nosniff` | Prevent MIME type sniffing |
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `X-XSS-Protection` | `1; mode=block` | Enable browser XSS filter |
| `Strict-Transport-Security` | `max-age=31536000` | Force HTTPS (when `HTTPS_ONLY=true`) |
| `Content-Security-Policy` | `default-src 'self'` | Restrict resource loading |

---

## Rate Limiting

API rate limiting is powered by `slowapi`:

| Setting | Default | Description |
|---|---|---|
| `RATE_LIMIT_DEFAULT` | `100/minute` | Default limit per IP |
| `RATE_LIMIT_ENABLED` | `true` | Toggle rate limiting |

Rate limit headers are returned in every response:
- `X-RateLimit-Limit` — Maximum requests per window
- `X-RateLimit-Remaining` — Remaining requests in current window
- `X-RateLimit-Reset` — Window reset timestamp

---

## Security Middleware Stack

The FastAPI middleware pipeline processes requests in this order:

1. **CORS** — Cross-origin request handling (`CORS_ORIGINS`)
2. **HTTPS Redirect** — Forces HTTPS when `HTTPS_ONLY=true`
3. **Security Headers** — Injects all security headers
4. **Rate Limiting** — Enforces per-IP rate limits
5. **JWT Validation** — Verifies EAT token signature and claims
6. **Semantic Scope Check** — Validates semantic scopes against the requested operation
7. **Prometheus Instrumentation** — Records request metrics

---

## CLI Commands

```bash
# Authenticate
engram auth login
engram auth login --token <eat-token>

# View identity and permissions
engram auth whoami
engram auth scope
engram auth status

# Manually set token
engram auth token-set <token>
```

---

## What's Next

- **[Configuration](./07-configuration.md)** — Configure security settings
- **[Architecture](./17-architecture.md)** — System-level security architecture
- **[SDK & Python Library](./16-sdk-python-library.md)** — Programmatic authentication
