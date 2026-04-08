# Learning Path

This page helps you find the right documentation based on your experience level and goals. Engram has a lot of surface area — from basic tool registration to ML-driven self-evolving tools — so this guide ensures you don't waste time on sections you don't need yet.

---

## Start Here

If you haven't installed Engram yet, begin with the [Installation](./02-installation.md) guide and then run through the [Quickstart](./01-quickstart.md). Everything below assumes you have a working installation with at least one tool registered.

---

## How to Use This Page

- **Know your level?** Jump to the experience-level table and follow the reading order for your tier.
- **Have a specific goal?** Skip to "By Use Case" and find the scenario that matches.
- **Just browsing?** Check the "Key Features" table for a quick overview of everything Engram can do.

---

## By Experience Level

| Level | Goal | Recommended Reading | Time Estimate |
|---|---|---|---|
| **Beginner** | Install, register first tool, test routing | Installation → Quickstart → CLI Reference → Configuration | ~1 hour |
| **Intermediate** | Set up healing, connect multiple protocols, deploy with Docker | Universal Onboarding → Self-Healing Engine → Hybrid Routing → Docker Setup → Observability | ~2–3 hours |
| **Advanced** | Build custom adapters, extend the SDK, deploy at scale, contribute | Architecture → SDK & Python Library → Protocol Federation → Self-Evolving Tools → Contributing | ~4–6 hours |

---

## By Use Case

### "I want to connect my agents to APIs reliably"

Use Engram as the semantic middleware between your agents and any API, ensuring tools stay working as APIs evolve.

**Reading order:**
1. [Installation](./02-installation.md)
2. [Quickstart](./01-quickstart.md)
3. [Universal Onboarding](./08-universal-onboarding.md)
4. [Self-Healing Engine](./09-self-healing-engine.md)
5. [Configuration](./07-configuration.md)

> **Tip:** Register tools via OpenAPI specs for the fastest path. Engram auto-generates dual MCP and CLI representations and begins monitoring for schema drift immediately.

### "I want intelligent routing between MCP and CLI"

Let Engram automatically choose the best execution backend for each task based on historical performance data.

**Reading order:**
1. [Quickstart](./01-quickstart.md)
2. [Hybrid Routing](./10-hybrid-routing.md)
3. [Observability & Tracing](./14-observability-tracing.md)
4. [Configuration](./07-configuration.md) (routing weights section)

### "I want agents to communicate across protocols"

Bridge MCP, CLI, A2A, and ACP agents seamlessly with ontology-backed translation.

**Reading order:**
1. [Protocol Federation](./11-protocol-federation.md)
2. [EAT Identity & Security](./12-eat-identity-security.md)
3. [Bidirectional Sync](./13-bidirectional-sync.md)
4. [Architecture](./17-architecture.md)

> **Tip:** Protocol federation uses the OWL ontology as a canonical bridge between protocols. Payloads are normalized through semantic concepts, not brittle field mappings.

### "I want to deploy Engram in production"

Run Engram at scale with Docker Compose or Kubernetes, full observability, and hardened security.

**Reading order:**
1. [Docker & Kubernetes Setup](./03-docker-kubernetes.md)
2. [Configuration](./07-configuration.md)
3. [EAT Identity & Security](./12-eat-identity-security.md)
4. [Observability & Tracing](./14-observability-tracing.md)
5. [Updating & Uninstalling](./04-updating-uninstalling.md)

### "I want to integrate Engram into my Python app"

Use the Engram SDK to programmatically register tools, translate payloads, manage tasks, and build agent workflows.

**Reading order:**
1. [Installation](./02-installation.md)
2. [SDK & Python Library](./16-sdk-python-library.md)
3. [Architecture](./17-architecture.md)
4. [EAT Identity & Security](./12-eat-identity-security.md)

### "I want to contribute to Engram"

Set up a development environment, understand the codebase structure, and submit your first PR.

**Reading order:**
1. [Installation](./02-installation.md) (manual setup)
2. [Architecture](./17-architecture.md)
3. [Contributing](./19-contributing.md)

---

## Key Features at a Glance

| Feature | What It Does | Docs Link |
|---|---|---|
| **Universal Onboarding** | Register any OpenAPI, GraphQL, CLI tool, or freeform docs as a dual MCP+CLI tool | [Universal Onboarding](./08-universal-onboarding.md) |
| **Self-Healing Engine** | OWL ontologies + ML detect and fix schema drift, field mismatches, and output changes in real time | [Self-Healing Engine](./09-self-healing-engine.md) |
| **Hybrid MCP+CLI Routing** | Performance-weighted routing chooses the best backend (MCP for structure, CLI for speed) per task | [Hybrid Routing](./10-hybrid-routing.md) |
| **Protocol Federation** | Seamless translation and handoff between MCP, CLI, A2A, and ACP with multi-hop support | [Protocol Federation](./11-protocol-federation.md) |
| **EAT Identity** | Unified Engram Authorization Token with structured permissions and semantic scopes from the ontology | [EAT Identity & Security](./12-eat-identity-security.md) |
| **Bidirectional Sync** | Event-driven synchronization across connected systems with semantic normalization and conflict resolution | [Bidirectional Sync](./13-bidirectional-sync.md) |
| **Observability & Tracing** | Rich semantic traces with routing reasoning, ontology alignment, healing steps, and LLM-generated summaries | [Observability & Tracing](./14-observability-tracing.md) |
| **Self-Evolving Tools** | ML continuously improves tool descriptions, parameter schemas, default values, and recovery strategies | [Self-Evolving Tools](./15-self-evolving-tools.md) |
| **Swarm Memory** | Persistent, ontology-aware fact store with Prolog reasoning and pyDatalog conflict resolution | [Architecture](./17-architecture.md) |
| **Delegation Engine** | Native agent delegation and orchestration with natural-language intent detection and sub-task routing | [Architecture](./17-architecture.md) |
| **SDK & Python Library** | Programmatic access to all Engram capabilities: auth, translation, task execution, tool registration | [SDK & Python Library](./16-sdk-python-library.md) |
| **Playground** | Web-based sandbox UI for testing translations and exploring the tool catalog without authentication | [Architecture](./17-architecture.md) |

---

## What to Read Next

- **Just finished installing?** → Head to the [Quickstart](./01-quickstart.md) to register your first tool.
- **Completed the Quickstart?** → Read the [CLI Reference](./06-cli-reference.md) and [Configuration](./07-configuration.md) to customize your setup.
- **Comfortable with the basics?** → Explore [Universal Onboarding](./08-universal-onboarding.md), [Self-Healing Engine](./09-self-healing-engine.md), and [Hybrid Routing](./10-hybrid-routing.md) to unlock the full power of the bridge.
- **Setting up for production?** → Read [Docker & Kubernetes Setup](./03-docker-kubernetes.md) and [EAT Identity & Security](./12-eat-identity-security.md).
- **Ready to build?** → Jump into the [SDK & Python Library](./16-sdk-python-library.md) and [Architecture](./17-architecture.md) to understand the internals.
- **Want practical examples?** → Check the `examples/` directory for tool registration scripts, SDK usage, and adapter patterns.

> **Tip:** You don't need to read everything. Pick the path that matches your goal, follow the links in order, and you'll be productive quickly. You can always come back to this page to find your next step.
