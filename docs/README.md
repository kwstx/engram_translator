# Engram Documentation

> **The semantic layer that connects any agent to any tool or API — reliably.**

Welcome to the Engram documentation. These guides cover everything from a 5-minute quickstart to deep dives into the self-healing engine, protocol federation, and ML-driven tool evolution.

---

## Getting Started

| Page | Description | Time |
|---|---|---|
| [Quickstart](./01-quickstart.md) | Install, register your first tool, test routing | ~5 min |
| [Installation](./02-installation.md) | Full installation guide with manual setup and troubleshooting | ~15 min |
| [Docker & Kubernetes](./03-docker-kubernetes.md) | Production deployment with containers | ~20 min |
| [Updating & Uninstalling](./04-updating-uninstalling.md) | Keep current or remove cleanly | ~5 min |
| [Learning Path](./05-learning-path.md) | Find the right docs for your experience level | ~5 min |

## Reference

| Page | Description |
|---|---|
| [CLI Reference](./06-cli-reference.md) | Every command, flag, REPL feature, and TUI dashboard |
| [Configuration](./07-configuration.md) | All 80+ settings with types, defaults, and examples |

## Features

| Page | Description |
|---|---|
| [Universal Onboarding](./08-universal-onboarding.md) | Register any API, CLI tool, or docs as a dual MCP+CLI tool |
| [Self-Healing Engine](./09-self-healing-engine.md) | OWL ontologies + ML detect and fix schema drift |
| [Hybrid Routing](./10-hybrid-routing.md) | Performance-weighted backend selection (MCP vs CLI) |
| [Protocol Federation](./11-protocol-federation.md) | Cross-protocol translation (MCP, CLI, A2A, ACP) |
| [EAT Identity & Security](./12-eat-identity-security.md) | Authentication, authorization, and the EAT token system |
| [Bidirectional Sync](./13-bidirectional-sync.md) | Event-driven synchronization with conflict resolution |
| [Observability & Tracing](./14-observability-tracing.md) | Semantic traces, Prometheus, Grafana, Sentry |
| [Self-Evolving Tools](./15-self-evolving-tools.md) | ML-driven continuous tool improvement |

## Advanced

| Page | Description |
|---|---|
| [SDK & Python Library](./16-sdk-python-library.md) | Programmatic access to all Engram capabilities |
| [Architecture](./17-architecture.md) | System internals, data flows, and design decisions |
| [Reliability Middleware](./18-reliability-middleware.md) | Circuit breakers, retry, idempotency |
| [Contributing](./19-contributing.md) | Development setup, code style, and PR guidelines |

---

## Quick Links

```bash
engram run                              # Start the gateway
engram register openapi <url>           # Register a tool
engram tools list                       # List all tools
engram route test "your task here"      # Test routing
engram heal status                      # Check self-healing
engram trace detail .                   # Inspect latest trace
engram auth whoami                      # View your identity
```
