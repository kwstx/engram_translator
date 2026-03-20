# MiroFish Swarm Bridge for Engram

We’re building a native MiroFish Swarm Bridge for Engram — a lightweight, one-line router that lets AI agents (like those from OpenClaw or Clawdbot ecosystems) instantly pipe inter-agent messages, live external data (news headlines, real-time prices, sentiment scores), and trading signals directly into a running MiroFish swarm simulation. By connecting to a user’s own local or self-hosted MiroFish instance (running on their machine with their personal LLM API key), the bridge injects clean, semantically preserved context into the swarm’s seed text and God’s-eye variables, keeps thousands to millions of digital agents perfectly synchronized without drift, and pipes the resulting high-fidelity swarm predictions back to the originating agent for immediate execution — turns simple prediction-market bots into powerful, real-time predict + execute hybrid systems in seconds.

## Getting Started

To initialize the bridge during development, follow these steps:

1.  **Ensure Node.js 18+** is installed on your system.
2.  **Install dependencies**: Run `npm install` in the root directory.
3.  **Launch the Services**:
    - **Docker (Recommended)**: Run `docker compose up -d --build`. This starts all components, including the backend bridge and the playground frontend.
    - **Individual Components**: Alternatively, run `npm run dev` in the root directory.
4.  **Verification**:
    - The **Backend REST service** (MiroFish Bridge) will be accessible at `http://localhost:5001`.
    - The **Frontend Playground** will run on port `3000`.

This setup is optimized for external piping discovery operations during your development testing only.

## Step 9 — Router Integration

The MiroFish bridge is now fully wired into the core Engram message routing system.  When the **target platform** equals `mirofish`, the Orchestrator automatically normalises the payload through the existing translation layer and forwards it to the user's MiroFish swarm instance.

### Prerequisites

> **Users must first launch their own MiroFish instance** with a valid `LLM_API_KEY` configured in its `.env` file.  Without a running MiroFish backend the router will return a connection error.

### One-Line Configuration (TypeScript — OpenClaw / Clawdbot)

```ts
import { engram } from './mirofish-bridge';

// Immediately send a message
const report = await engram.routeTo('mirofish', {
  swarmId: 'prediction-market-1',
  mirofishBaseUrl: 'http://localhost:5001',
}, 'Analyse upcoming ETH merge impact');

// Or get a re-usable sender
const sendToSwarm = await engram.routeTo('mirofish', {
  swarmId: 'prediction-market-1',
  mirofishBaseUrl: 'http://localhost:5001',
});
const report2 = await sendToSwarm('Another inter-agent message');
```

### Python Backend — Orchestrator Routing

On the server side, passing `target_protocol="mirofish"` to the Orchestrator triggers the same bridge:

```python
from app.messaging.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Sync path (e.g. from TaskWorker):
result = orchestrator.handoff(
    source_message={
        "intent": "predict",
        "content": "BTC 7-day forecast",
        "metadata": {
            "swarmId": "crypto-swarm",
            "mirofishBaseUrl": "http://localhost:5001",
            "numAgents": 500,
            "externalData": {"prices": [{"symbol": "BTC/USD", "price": "64200"}]}
        }
    },
    source_protocol="A2A",
    target_protocol="mirofish",
)

# Async path (e.g. from a FastAPI route):
result = await orchestrator.handoff_async(
    source_message=payload,
    source_protocol="MCP",
    target_protocol="mirofish",
)
```

### Environment Configuration

Add these to your `.env` (all optional — sensible defaults are applied):

| Variable | Default | Description |
|---|---|---|
| `MIROFISH_BASE_URL` | `http://localhost:5001` | MiroFish service base URL |
| `MIROFISH_DEFAULT_NUM_AGENTS` | `1000` | Default swarm size |
| `MIROFISH_DEFAULT_SWARM_ID` | `default` | Default swarm identifier |

### Semantic Fidelity

All payloads are run through the existing `TranslatorEngine` translation layer before injection.  This means any A2A, MCP, or ACP message is normalised to MCP format first, preserving semantic fidelity regardless of the originating protocol.

### How It Works

1. The caller passes `target_protocol="mirofish"` (case-insensitive) to the Orchestrator.
2. The Orchestrator detects the `MIROFISH` target and short-circuits the normal protocol graph.
3. `pipe_to_mirofish_swarm()` (in `app/services/mirofish_router.py`) normalises the payload via `TranslatorEngine`.
4. The normalised payload is POSTed to the user's MiroFish `/api/simulation/start` endpoint.
5. The compiled simulation report is returned as the `HandoffResult.translated_message`.

### File Map

| File | Purpose |
|---|---|
| `app/services/mirofish_router.py` | Python-side router — normalises + HTTP POST to MiroFish |
| `app/messaging/orchestrator.py` | Orchestrator conditional: `if tgt == "MIROFISH"` |
| `app/core/config.py` | `MIROFISH_BASE_URL`, `MIROFISH_DEFAULT_NUM_AGENTS`, `MIROFISH_DEFAULT_SWARM_ID` |
| `playground/src/mirofish-bridge.ts` | TypeScript `engram.routeTo('mirofish', ...)` one-liner |
