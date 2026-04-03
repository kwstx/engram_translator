# Semantic Bridge

The adaptive semantic interoperability layer for AI agents. Connect **anything** — any API, any system, any protocol — with one lightweight layer that auto-generates tools, self-heals schema drift, intelligently routes between MCP and CLI, and scales seamlessly from single agents to multi-agent swarms.

It creates reliable, self-improving tool integrations: register once (or point at any endpoint), and your agents get tools that adapt over time, fix mismatches on the fly, choose the best execution backend (MCP for structure or CLI for speed), and collaborate across protocols without glue code or maintenance hell.

**Universal onboarding** • **Self-healing schemas with OWL + ML** • **Hybrid MCP + CLI execution** • **Performance-weighted routing** • **Unified EAT identity** • **Bidirectional sync** • **Cross-protocol federation (A2A/ACP)** • **Self-evolving tools**

Works with any agent framework. No lock-in. Runs lightweight on your laptop, VPS, or in production.

## What It Does

Semantic Bridge solves brittle agent tool integrations that break in production. It sits between agents and tools, translating and routing across protocols while keeping integrations healthy over time:

- Translates between MCP, CLI, A2A, and ACP with multi-hop handoffs when needed.
- Auto-generates tool schemas and keeps them aligned as APIs drift.
- Chooses the best execution backend (structured MCP or faster CLI) per task.
- Maintains a unified EAT identity and permissions model across protocols.
- Syncs and normalizes events for reliable cross-system collaboration.

## Quick Install

```bash
curl -fsSL https://get.semanticbridge.dev/install | bash
```

Works on Linux, macOS, and WSL2. The installer sets up Python dependencies, the `sb` CLI, and core services.

After installation:

```bash
source ~/.bashrc    # or source ~/.zshrc
sb                  # start the CLI
```

## Getting Started

```bash
sb                  # Interactive CLI mode
sb register         # Onboard any API or CLI tool
sb tools list       # View all registered tools
sb route test "send an email"   # Test intelligent routing
sb doctor           # Check system health
sb update           # Update to latest version
```

## Core Features

1. Universal onboarding that accepts any OpenAPI, GraphQL, URL+auth, partial docs, or CLI manifest and auto-generates dual MCP + CLI representations.
2. Core self-healing engine using OWL ontologies + ML that detects and fixes schema drift, custom fields, and output mismatches in real time.
3. Unified EAT token with semantic permissions that works across MCP and CLI.
4. Basic performance-weighted routing that chooses the best backend (CLI for token efficiency or MCP for structured calls) based on task and history.
5. Bidirectional sync and event layer for any connected system with semantic normalization.
6. Context-aware pruning and rich semantic traces for observability.
7. Efficient support for popular apps while keeping custom and internal tools as the hero.
8. Self-evolving tools: ML continuously improves descriptions, defaults, and recovery strategies from real executions.
9. Full cross-protocol federation with seamless translation and handoff between MCP, CLI, A2A, and ACP.
10. Predictive optimizer and adaptive wrappers for legacy/non-API systems.

## CLI Command Reference

The `sb` CLI is your primary interface — clean, scriptable, and agent-friendly with Rich formatting and JSON output mode.

Add `--json` for machine-readable output perfect for agents. Run `sb <command> --help` for detailed flags.

## Why It’s Different

Most tool platforms give you connectors that break on custom fields or API changes. Semantic Bridge gives agents tools that heal themselves, intelligently pick between MCP and CLI, evolve over time, and work across protocols — so your agents stay reliable in production without constant maintenance.

## Documentation

Full documentation lives at docs.semanticbridge.dev:

- Quickstart — Install to first connected tool in under 5 minutes
- CLI Reference — All commands and flags
- Universal Onboarding — How to connect any API or CLI tool
- Self-Healing Engine — OWL ontologies + ML explained
- MCP + CLI Hybrid Routing — When each backend is chosen
- Protocol Federation — A2A and ACP handoff
- Configuration — EAT tokens, routing weights, ontology
- Architecture — Phases, components, and design decisions
- Contributing — Development setup and guidelines

Built for developers who want agents that actually work on real-world systems — not just popular SaaS.

Star the repo if you’re building reliable agent tooling.
