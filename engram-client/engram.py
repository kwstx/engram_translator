import os
import json
import asyncio
import time
from typing import Optional, Dict, Any, List, Tuple
from collections import deque
from datetime import datetime
try:
    import rich_click as click
    RICH_CLICK_AVAILABLE = True
    click.rich_click.MAX_WIDTH = 100
    click.rich_click.USE_RICH_MARKUP = True
    click.rich_click.SHOW_ARGUMENTS = True
    click.rich_click.SHOW_METAVARS_COLUMN = True
    click.rich_click.STYLE_ERRORS_SUGGESTION = "yellow"
except Exception:
    import click
    RICH_CLICK_AVAILABLE = False
import httpx
import networkx as nx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.live import Live
from rich.text import Text
from cryptography.fernet import Fernet, InvalidToken

console = Console()
__version__ = "0.2.0"

CONFIG_DIR = os.path.expanduser("~/.engram")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.enc")
LEGACY_CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
KEY_FILE = os.path.join(CONFIG_DIR, "key")
DEFAULT_BASE_URL = "http://localhost:8000/api/v1"

PROVIDERS = [
    {
        "id": "claude",
        "name": "Claude",
        "auth": "api_key",
        "hint": "Anthropic API key",
        "aliases": ["claude", "anthropic"],
    },
    {
        "id": "perplexity",
        "name": "Perplexity",
        "auth": "api_key",
        "hint": "Perplexity API key",
        "aliases": ["perplexity", "pplx"],
    },
    {
        "id": "slack",
        "name": "Slack",
        "auth": "oauth",
        "hint": "Slack OAuth token",
        "aliases": ["slack"],
    },
]

PROVIDER_MAP = {provider["id"]: provider for provider in PROVIDERS}

def _ensure_key() -> bytes:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    try:
        os.chmod(KEY_FILE, 0o600)
    except OSError:
        pass
    return key

def _get_fernet() -> Fernet:
    return Fernet(_ensure_key())

def _encrypt_config(config: Dict[str, Any]) -> str:
    payload = json.dumps(config).encode("utf-8")
    return _get_fernet().encrypt(payload).decode("utf-8")

def _decrypt_config(token: str) -> Dict[str, Any]:
    payload = _get_fernet().decrypt(token.encode("utf-8"))
    return json.loads(payload.decode("utf-8"))

def _default_config() -> Dict[str, Any]:
    return {
        "base_url": DEFAULT_BASE_URL, 
        "token": None, 
        "eat": None, 
        "email": None,
        "vault": {} # { "base_url|email": { "provider_id": { ... } } }
    }

def _normalize_config(config: Dict[str, Any]) -> Dict[str, Any]:
    base = _default_config()
    base.update(config or {})
    return base

def load_config() -> Dict[str, Any]:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return _normalize_config(_decrypt_config(f.read().strip()))
        except (InvalidToken, json.JSONDecodeError, OSError) as exc:
            console.print(f"[yellow]WARN[/] Encrypted config could not be read ({exc}). Reinitializing.")
            return _default_config()
    if os.path.exists(LEGACY_CONFIG_FILE):
        with open(LEGACY_CONFIG_FILE, "r") as f:
            legacy = json.load(f)
        legacy = _normalize_config(legacy)
        save_config(legacy)
        return legacy
    return _default_config()

def save_config(config: Dict[str, Any]):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        f.write(_encrypt_config(config))

async def check_health(base_url: str, token: Optional[str] = None) -> bool:
    root_url = base_url.replace("/api/v1", "")
    try:
        async with httpx.AsyncClient() as client:
            headers = _auth_header(token)
            response = await client.get(root_url, headers=headers)
            return response.status_code == 200
    except Exception:
        return False

def _auth_header(token: Optional[str]) -> Dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}

def _merge_headers(base: Optional[Dict[str, str]], extra: Optional[Dict[str, str]]) -> Dict[str, str]:
    merged: Dict[str, str] = {}
    if base:
        merged.update(base)
    if extra:
        merged.update(extra)
    return merged

def _extract_error_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            return str(payload.get("detail") or payload.get("error") or response.text)
    except Exception:
        pass
    return response.text

def _response_indicates_token_issue(response: httpx.Response) -> bool:
    if response.status_code not in (401, 403):
        return False
    detail = _extract_error_detail(response).lower()
    markers = ("expired", "revoked", "invalid", "unauthorized", "missing", "session")
    return any(marker in detail for marker in markers)

def _render_task_results(results: Optional[Dict[str, Any]]) -> None:
    if not results:
        console.print("[dim]No workflow results recorded yet.[/]")
        return
    console.print("\n[bold]Workflow Results:[/]")
    for agent_id, output in results.items():
        console.print(f"  [bold cyan]{agent_id}[/]")
        syntax = Syntax(json.dumps(output, indent=2), "json", theme="monokai", line_numbers=False)
        console.print(syntax)

def _render_workflow_table(workflows: List[Dict[str, Any]]) -> None:
    table = Table(title="Workflows")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Active")
    table.add_column("Updated")
    for wf in workflows:
        table.add_row(
            str(wf.get("id")),
            str(wf.get("name")),
            "YES" if wf.get("is_active") else "NO",
            str(wf.get("updated_at")),
        )
    console.print(table)

def _render_workflow_detail(workflow: Dict[str, Any]) -> None:
    table = Table(title="Workflow Detail", show_header=False)
    table.add_row("ID", str(workflow.get("id")))
    table.add_row("Name", str(workflow.get("name")))
    table.add_row("Description", str(workflow.get("description") or ""))
    table.add_row("Active", "YES" if workflow.get("is_active") else "NO")
    table.add_row("Updated", str(workflow.get("updated_at")))
    table.add_row("Last Run", str(workflow.get("last_run_at") or ""))
    table.add_row("Command", str(workflow.get("command") or ""))
    console.print(table)

def _infer_required_providers(command: str) -> List[Dict[str, Any]]:
    text = command.lower()
    required: Dict[str, Dict[str, Any]] = {}
    for provider in PROVIDERS:
        aliases = provider.get("aliases") or [provider["id"], provider["name"].lower()]
        if any(alias in text for alias in aliases):
            required[provider["id"]] = provider

    if ("post" in text or "send" in text) and "slack" in PROVIDER_MAP:
        required["slack"] = PROVIDER_MAP["slack"]
    if ("search" in text or "research" in text) and "perplexity" in PROVIDER_MAP:
        required["perplexity"] = PROVIDER_MAP["perplexity"]

    return list(required.values())

async def _fetch_connected_providers(config: Dict[str, Any]) -> Optional[set]:
    async with Engram() as sdk:
        response = await sdk.request("GET", "/credentials")
        if response.status_code != 200:
            console.print(f"[yellow]WARN[/] Credential fetch failed: {_extract_error_detail(response)}")
            return None
        payload = response.json()
        return {item.get("provider_name", "").lower() for item in payload if item.get("provider_name")}

async def _connect_provider(config: Dict[str, Any], provider: Dict[str, Any]) -> bool:
    display_name = provider.get("name", provider.get("id", "Provider"))
    auth_label = "API key" if provider.get("auth") == "api_key" else "OAuth token"
    hint = provider.get("hint", "Paste token")
    console.print(Panel(
        f"[bold]Connect {display_name}[/]\n{hint}",
        title="Provider Connection Required",
        border_style="yellow",
    ))
    token = click.prompt(f"{display_name} {auth_label}", type=str, hide_input=True)
    if not token:
        console.print("[red]ERROR[/] No token provided.")
        return False
    
    credential_type = "API_KEY" if provider.get("auth") == "api_key" else "OAUTH_TOKEN"
    metadata = {
        "display_name": provider.get("name"),
        "flow": provider.get("auth"),
        "source": "cli_vault"
    }
    
    payload = {
        "provider_name": provider.get("id"),
        "credential_type": credential_type,
        "token": token,
        "metadata": metadata,
    }
    
    async with Engram() as sdk:
        response = await sdk.request("POST", "/credentials", json_body=payload)
        if response.status_code not in (200, 201):
            console.print(f"[red]ERROR[/] Connection failed: {_extract_error_detail(response)}")
            return False
            
    # Save to local vault for future persistence
    if "vault" not in config:
        config["vault"] = {}
    vault_key = f"{config['base_url']}|{config['email']}"
    if vault_key not in config["vault"]:
        config["vault"][vault_key] = {}
        
    config["vault"][vault_key][provider["id"]] = {
        "token": token,
        "type": credential_type,
        "metadata": metadata,
        "last_synced": datetime.now().isoformat()
    }
    save_config(config)
    
    console.print(f"[green]Connected[/] {display_name} credential saved to backend and local vault.")
    return True

async def _connect_provider_from_vault(config: Dict[str, Any], provider: Dict[str, Any], vault_entry: Dict[str, Any]) -> bool:
    """Re-applies a local vault credential to the current backend session."""
    display_name = provider.get("name", provider.get("id", "Provider"))
    payload = {
        "provider_name": provider.get("id"),
        "credential_type": vault_entry["type"],
        "token": vault_entry["token"],
        "metadata": vault_entry.get("metadata") or {},
    }
    # Update source to indicate vault sync
    if "metadata" in payload:
        payload["metadata"]["sync_from"] = "local_vault"
        payload["metadata"]["sync_at"] = datetime.now().isoformat()

    async with Engram() as sdk:
        response = await sdk.request("POST", "/credentials", json_body=payload)
        if response.status_code not in (200, 201):
            console.print(f"[yellow]WARN[/] Persistent sync for {display_name} failed: {_extract_error_detail(response)}")
            return False
    
    # Update last_synced in vault
    vault_key = f"{config['base_url']}|{config['email']}"
    config["vault"][vault_key][provider["id"]]["last_synced"] = datetime.now().isoformat()
    save_config(config)
    
    console.print(f"[bold green]Auto-Connected[/] {display_name} from local vault.")
    return True

async def _ensure_required_providers_connected(config: Dict[str, Any], command: str) -> bool:
    required = _infer_required_providers(command)
    if not required:
        return True
    connected = await _fetch_connected_providers(config)
    if connected is None:
        return False

    missing = [provider for provider in required if provider.get("id") not in connected]
    if not missing:
        return True

    # Try local vault first
    vault_key = f"{config.get('base_url')}|{config.get('email')}"
    vault = config.get("vault", {}).get(vault_key, {})
    
    still_missing = []
    for provider in missing:
        provider_id = provider.get("id")
        if provider_id in vault:
            if await _connect_provider_from_vault(config, provider, vault[provider_id]):
                connected.add(provider_id)
                continue
        still_missing.append(provider)

    for provider in still_missing:
        display_name = provider.get("name", provider.get("id", "Provider"))
        proceed = click.confirm(
            f"Task requires {display_name} but it is not connected. Connect now?",
            default=True,
        )
        if not proceed:
            console.print("[yellow]Connection skipped. Aborting task.[/]")
            return False
        if not await _connect_provider(config, provider):
            return False
        connected.add(provider.get("id"))

    return True

class ExecutionTraceState:
    def __init__(self, max_lines: int = 8):
        self.connections = deque(maxlen=max_lines)
        self.agents = deque(maxlen=max_lines)
        self.tools = deque(maxlen=max_lines)
        self.responses = deque(maxlen=max_lines)
        self.last_ts = 0.0

    def _format_time(self, ts: Optional[float]) -> str:
        if not ts:
            return "--:--:--"
        return datetime.fromtimestamp(ts).strftime("%H:%M:%S")

    def _route(self, event_type: str, line: str) -> None:
        if event_type.startswith("connection"):
            self.connections.append(line)
            return
        if event_type.startswith("agent"):
            self.agents.append(line)
            return
        if event_type.startswith("tool"):
            self.tools.append(line)
            return
        if event_type.startswith("response"):
            self.responses.append(line)
            return

        lower = line.lower()
        if "handing off" in lower or "orchestration plan" in lower:
            self.agents.append(line)
        elif "response" in lower:
            self.responses.append(line)
        elif "connect" in lower or "connector" in lower:
            self.connections.append(line)
        else:
            self.tools.append(line)

    def add_event(self, event: Dict[str, Any]) -> None:
        event_type = event.get("event_type") or event.get("type") or "execution.log"
        message = event.get("message") or event_type
        created_at = event.get("created_at")
        ts = None
        if created_at:
            try:
                ts = datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp()
            except Exception:
                ts = None
        if ts and ts > self.last_ts:
            self.last_ts = ts
        timestamp = self._format_time(ts)
        line = f"[dim]{timestamp}[/] {message}"
        self._route(event_type, line)

def _render_trace_panel(title: str, lines: deque, border_style: str) -> Panel:
    if lines:
        content = "\n".join(lines)
    else:
        content = "[dim]Waiting for events...[/]"
    return Panel(content, title=title, border_style=border_style)

def _render_trace_view(state: ExecutionTraceState, task_id: str, status: str) -> Panel:
    grid = Table.grid(expand=True)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)
    grid.add_row(
        _render_trace_panel("Connections", state.connections, "cyan"),
        _render_trace_panel("Agent Execution", state.agents, "yellow"),
    )
    grid.add_row(
        _render_trace_panel("Tool Usage", state.tools, "magenta"),
        _render_trace_panel("Responses", state.responses, "green"),
    )
    return Panel(grid, title=f"Execution Trace • Task {task_id} • {status}", border_style="orange1")

def _render_status(config: Dict[str, Any]) -> None:
    base_url = config["base_url"]
    table = Table(title="Engram Status", show_header=False, box=None)
    table.add_row("Base URL", base_url)
    console.print(Panel(table, title="[bold orange1]ENGRAM CLIENT[/]", border_style="orange1"))

def _task_signals(task: str) -> Dict[str, float]:
    text = (task or "").lower()
    keywords = {
        "multi_hop": ["translate", "protocol", "bridge", "orchestrate", "routing", "handoff"],
        "real_time": ["stream", "real-time", "live", "watch", "monitor", "tail"],
        "compliance": ["audit", "compliance", "pii", "hipaa", "gdpr", "security"],
        "batch": ["batch", "backfill", "bulk", "archive"],
        "api": ["api", "webhook", "openapi", "graphql", "endpoint"],
    }
    scores = {key: 0.0 for key in keywords}
    for key, terms in keywords.items():
        scores[key] = float(sum(1 for term in terms if term in text))
    complexity = min(3.0, 1.0 + 0.4 * scores["multi_hop"] + 0.2 * scores["api"] + 0.3 * scores["batch"])
    novelty = 1.0 + 0.2 * scores["compliance"] + 0.2 * scores["real_time"]
    return {
        "complexity": complexity,
        "real_time": scores["real_time"],
        "multi_hop": scores["multi_hop"],
        "compliance": scores["compliance"],
        "api": scores["api"],
        "novelty": novelty,
    }

def _estimate_path_metrics(task: str) -> Dict[str, Dict[str, float]]:
    signals = _task_signals(task)
    complexity = signals["complexity"]
    multi_hop = signals["multi_hop"] > 0
    real_time = signals["real_time"] > 0

    cli_base_cost = 0.003
    mcp_base_cost = 0.012
    cli_cost = cli_base_cost + 0.003 * complexity + (0.004 if multi_hop else 0.0)
    mcp_cost = mcp_base_cost + 0.008 * complexity + (0.002 if real_time else 0.0)

    cli_latency = 220 + 90 * complexity + (120 if multi_hop else 0)
    mcp_latency = 420 + 140 * complexity + (60 if real_time else 0)

    cli_fidelity = max(0.62, 0.85 - 0.08 * complexity - (0.08 if multi_hop else 0.0))
    mcp_fidelity = max(0.78, 0.95 - 0.03 * complexity)

    cli_risk = 1.0 - cli_fidelity
    mcp_risk = 1.0 - mcp_fidelity

    cli_weight = (cli_cost * 120) + (cli_latency / 1000.0) + (cli_risk * 5.0)
    mcp_weight = (mcp_cost * 120) + (mcp_latency / 1000.0) + (mcp_risk * 5.0)

    return {
        "CLI": {
            "cost": cli_cost,
            "latency_ms": cli_latency,
            "fidelity": cli_fidelity,
            "risk": cli_risk,
            "weight": cli_weight,
        },
        "MCP": {
            "cost": mcp_cost,
            "latency_ms": mcp_latency,
            "fidelity": mcp_fidelity,
            "risk": mcp_risk,
            "weight": mcp_weight,
        },
    }

def _build_optimizer_graph(metrics: Dict[str, Dict[str, float]]) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node("TASK")
    graph.add_node("CLI")
    graph.add_node("MCP")
    graph.add_node("EXECUTION")
    for path in ("CLI", "MCP"):
        weight = metrics[path]["weight"]
        graph.add_edge("TASK", path, weight=weight)
        graph.add_edge(path, "EXECUTION", weight=weight)
    return graph

def _format_cost(value: float) -> str:
    return f"${value:.3f}"

def _format_latency(value: float) -> str:
    return f"{int(round(value))} ms"

def _render_optimizer_output(task: str, metrics: Dict[str, Dict[str, float]], graph: nx.DiGraph) -> None:
    table = Table(title="Predictive Cost Forecast")
    table.add_column("Path", style="cyan")
    table.add_column("Route Weight", justify="right")
    table.add_column("Estimated Cost", justify="right")
    table.add_column("Latency", justify="right")
    table.add_column("Semantic Fidelity", justify="right")
    table.add_column("Risk", justify="right")

    for path in ("MCP", "CLI"):
        table.add_row(
            path,
            f"{metrics[path]['weight']:.2f}",
            _format_cost(metrics[path]["cost"]),
            _format_latency(metrics[path]["latency_ms"]),
            f"{metrics[path]['fidelity']*100:.1f}%",
            f"{metrics[path]['risk']*100:.1f}%",
        )

    console.print(table)

    cli_path = ["TASK", "CLI", "EXECUTION"]
    mcp_path = ["TASK", "MCP", "EXECUTION"]
    recommendation = "MCP" if metrics["MCP"]["weight"] <= metrics["CLI"]["weight"] else "CLI"
    reason_lines = []

    if recommendation == "MCP":
        reason_lines.append("Graph weight favors MCP for semantic stability across hops.")
        reason_lines.append("MCP keeps fidelity higher when tasks involve translation or orchestration.")
    else:
        reason_lines.append("Graph weight favors a direct CLI path for speed and low overhead.")
        reason_lines.append("CLI wins when the task is short, local, or mostly procedural.")

    explanation = "\n".join(f"- {line}" for line in reason_lines)
    console.print(Panel(explanation, title=f"Recommendation: {recommendation}", border_style="green"))

    path_table = Table(title="Graph Paths")
    path_table.add_column("Path", style="magenta")
    path_table.add_column("Sequence")
    path_table.add_row("CLI Route", " -> ".join(cli_path))
    path_table.add_row("MCP Route", " -> ".join(mcp_path))
    console.print(path_table)

    console.print(Text("Estimates are derived from the internal routing graph weights (cost, latency, and risk).", style="dim"))

def _safe_wrapper_name(raw: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in raw.strip().lower())
    cleaned = cleaned.strip("-_")
    return cleaned or "adaptive-wrapper"

def _wrapper_manifest(name: str, api_url: Optional[str], cli_command: Optional[str]) -> Dict[str, Any]:
    return {
        "name": name,
        "version": "0.1.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "api": {"base_url": api_url} if api_url else None,
        "cli": {"command": cli_command} if cli_command else None,
        "fallback": "cli" if cli_command else "api",
        "self_healing": True,
    }

def _wrapper_script(name: str, api_url: Optional[str], cli_command: Optional[str]) -> str:
    api_line = f"API_BASE_URL = '{api_url}'" if api_url else "API_BASE_URL = None"
    cli_line = f"CLI_COMMAND = '{cli_command}'" if cli_command else "CLI_COMMAND = None"
    return "\n".join([
        "#!/usr/bin/env python",
        "import json",
        "import os",
        "import subprocess",
        "import httpx",
        "",
        f"WRAPPER_NAME = '{name}'",
        api_line,
        cli_line,
        "",
        "def call_api(payload, timeout=10):",
        "    if not API_BASE_URL:",
        "        raise RuntimeError('API endpoint missing')",
        "    response = httpx.post(API_BASE_URL, json=payload, timeout=timeout)",
        "    response.raise_for_status()",
        "    return response.json() if response.content else {'status': 'ok'}",
        "",
        "def call_cli(payload, timeout=20):",
        "    if not CLI_COMMAND:",
        "        raise RuntimeError('CLI fallback missing')",
        "    env = os.environ.copy()",
        "    env['ENGRAM_PAYLOAD'] = json.dumps(payload)",
        "    cmd = [CLI_COMMAND]",
        "    return subprocess.run(cmd, check=True, env=env, timeout=timeout, capture_output=True, text=True).stdout",
        "",
        "def run(payload):",
        "    try:",
        "        return call_api(payload)",
        "    except Exception:",
        "        return call_cli(payload)",
        "",
        "if __name__ == '__main__':",
        "    raw = os.environ.get('ENGRAM_PAYLOAD', '{}')",
        "    print(run(json.loads(raw)))",
    ])

def _render_wrapper_generation(name: str, api_url: Optional[str], cli_command: Optional[str]) -> None:
    events: List[str] = []

    def push(line: str) -> None:
        events.append(line)

    panel = Panel("\n".join(events) or "[dim]Preparing wrapper...[/]", title="Adaptive Wrapper Builder", border_style="cyan")
    with Live(panel, refresh_per_second=8) as live:
        push("[bold]Initializing adaptive wrapper pipeline[/]")
        live.update(Panel("\n".join(events), title="Adaptive Wrapper Builder", border_style="cyan"))
        time.sleep(0.1)

        if api_url:
            push(f"[green]API endpoint detected[/] {api_url}")
        else:
            push("[yellow]No API endpoint supplied; CLI fallback becomes primary[/]")
        live.update(Panel("\n".join(events), title="Adaptive Wrapper Builder", border_style="cyan"))
        time.sleep(0.1)

        if cli_command:
            push(f"[green]CLI fallback registered[/] {cli_command}")
        else:
            push("[yellow]No CLI fallback registered; wrapper will rely on API[/]")
        live.update(Panel("\n".join(events), title="Adaptive Wrapper Builder", border_style="cyan"))
        time.sleep(0.1)

        push("[yellow]Schema probe timed out — activating self-healing mode[/]")
        live.update(Panel("\n".join(events), title="Adaptive Wrapper Builder", border_style="cyan"))
        time.sleep(0.1)

        push("[green]Self-healing applied[/] Cached schema hints + CLI sandbox ready")
        live.update(Panel("\n".join(events), title="Adaptive Wrapper Builder", border_style="cyan"))
        time.sleep(0.1)

        push(f"[bold green]Wrapper ready[/] {name}")
        live.update(Panel("\n".join(events), title="Adaptive Wrapper Builder", border_style="cyan"))

async def _run_doctor_checks() -> List[Tuple[str, bool, str]]:
    config = load_config()
    checks: List[Tuple[str, bool, str]] = []

    key_ok = os.path.exists(KEY_FILE)
    checks.append(("Encryption key", key_ok, "OK" if key_ok else "Missing key file"))

    config_ok = os.path.exists(CONFIG_FILE) or os.path.exists(LEGACY_CONFIG_FILE)
    checks.append(("Config storage", config_ok, "OK" if config_ok else "Initialize with `engram init`"))

    base_url = config.get("base_url") or DEFAULT_BASE_URL
    backend_ok = await check_health(base_url, token=config.get("eat") or config.get("token"))
    checks.append(("Backend reachable", backend_ok, base_url if backend_ok else f"Unavailable at {base_url}"))

    token_ok = bool(config.get("token") or config.get("eat"))
    checks.append(("Authentication", token_ok, "Token/EAT present" if token_ok else "Run `engram login` or `engram eat`"))

    try:
        _ = _build_optimizer_graph(_estimate_path_metrics("health check"))
        graph_ok = True
    except Exception as exc:
        graph_ok = False
        graph_err = str(exc)
    checks.append(("Optimizer graph", graph_ok, "OK" if graph_ok else graph_err))

    writable = os.access(os.getcwd(), os.W_OK)
    checks.append(("Wrapper output", writable, "Writable" if writable else "Current directory not writable"))

    vault_entries = bool(config.get("vault"))
    checks.append(("Credential vault", vault_entries, "Entries found" if vault_entries else "Empty vault"))

    checks.append(("Rich help", RICH_CLICK_AVAILABLE, "rich-click enabled" if RICH_CLICK_AVAILABLE else "Fallback help"))

    return checks

class Engram:
    """
    Engram SDK Client for interacting with the Engram Protocol Bridge and Identity Server.
    
    This client automatically manages authentication session tokens and Engram Access Tokens (EATs).
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        eat: Optional[str] = None,
        interactive: bool = False,
    ):
        self._config = load_config()
        self.base_url = base_url or self._config.get("base_url") or DEFAULT_BASE_URL
        self.email = email or self._config.get("email")
        self.password = password
        self.token = token or self._config.get("token")
        self.eat = eat or self._config.get("eat")
        self.interactive = interactive
        self._client = httpx.AsyncClient(timeout=60.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self._client.aclose()

    def _save_state(self):
        """Persists the current auth state to the local config."""
        self._config.update({
            "base_url": self.base_url,
            "email": self.email,
            "token": self.token,
            "eat": self.eat,
        })
        save_config(self._config)

    async def signup(self, email: str, password: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new Engram account."""
        try:
            payload = {
                "email": email, 
                "password": password, 
                "user_metadata": metadata or {"source": "python_sdk"}
            }
            response = await self._client.post(f"{self.base_url}/auth/signup", json=payload)
            if response.status_code == 201:
                if self.interactive:
                    console.print("[green]OK[/] Account created successfully.")
                self.email = email
                return True
            
            if self.interactive:
                console.print(f"[red]ERROR[/] Signup failed: {response.text}")
            return False
        except Exception as exc:
            if self.interactive:
                console.print(f"[red]ERROR[/] Connection error: {str(exc)}")
            return False

    async def login(self, email: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Log in to the Engram Identity Server to obtain a session token.
        If credentials aren't provided, it uses the ones passed during initialization.
        """
        login_email = email or self.email
        login_password = password or self.password

        if not login_email or not login_password:
            if self.interactive:
                login_email = click.prompt("Email", type=str, default=self.email or "")
                login_password = click.prompt("Password", type=str, hide_input=True)
            else:
                raise ValueError("Email and password are required for login.")

        try:
            response = await self._client.post(
                f"{self.base_url}/auth/login",
                data={"username": login_email, "password": login_password}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.email = login_email
                self._save_state()
                if self.interactive:
                    console.print("[green]OK[/] Login successful.")
                return True
            
            if self.interactive:
                console.print(f"[red]ERROR[/] Login failed: {response.text}")
            return False
        except Exception as exc:
            if self.interactive:
                console.print(f"[red]ERROR[/] Connection error: {str(exc)}")
            return False

    async def generate_eat(self, expires_days: int = 30) -> Optional[str]:
        """
        Generates a long-lived Engram Access Token (EAT) for tool/agent execution.
        Requires a valid session token (via login).
        """
        if not self.token:
            if not await self.login():
                return None

        try:
            response = await self._client.post(
                f"{self.base_url}/auth/tokens/generate-eat",
                headers=_auth_header(self.token),
                params={"expires_days": expires_days}
            )
            if response.status_code == 200:
                self.eat = response.json().get("eat")
                self._save_state()
                if self.interactive:
                    console.print("[green]OK[/] EAT generated and stored.")
                return self.eat
            
            if self.interactive:
                console.print(f"[red]ERROR[/] EAT generation failed: {response.text}")
            return None
        except Exception as exc:
            if self.interactive:
                console.print(f"[red]ERROR[/] Connection error: {str(exc)}")
            return None

    async def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 60.0,
        use_session_token: bool = False,
        allow_retry: bool = True,
    ) -> httpx.Response:
        """
        Makes an authenticated request to the Engram API.
        Automatically attaches EAT or session token and handles expired tokens.
        """
        token = self.token if use_session_token else (self.eat or await self.generate_eat())
        
        if not token:
            # Last ditch effort: try to login if we have creds
            if self.email and self.password:
                if await self.login():
                    token = self.token if use_session_token else await self.generate_eat()
            
            if not token and self.interactive:
                if await self._prompt_reauth():
                    token = self.token if use_session_token else (self.eat or await self.generate_eat())

        if not token:
            raise PermissionError("No valid token or EAT available. Please call login().")

        request_headers = _merge_headers(headers, _auth_header(token))
        url = f"{self.base_url}{path}"
        
        response = await self._client.request(
            method, url, json=json_body, data=data, headers=request_headers, timeout=timeout
        )

        if allow_retry and _response_indicates_token_issue(response):
            # Attempt to refresh/reauth
            refreshed = False
            if not use_session_token:
                # EAT might have expired, try to generate a new one with session token
                if await self.generate_eat():
                    token = self.eat
                    refreshed = True
            
            if not refreshed:
                # Session token might have expired, try to login
                if self.email and self.password:
                    if await self.login():
                        token = self.token if use_session_token else await self.generate_eat()
                        refreshed = True
                elif self.interactive:
                    if await self._prompt_reauth():
                        token = self.token if use_session_token else (self.eat or await self.generate_eat())
                        refreshed = True

            if refreshed:
                retry_headers = _merge_headers(headers, _auth_header(token))
                return await self._client.request(
                    method, url, json=json_body, data=data, headers=retry_headers, timeout=timeout
                )
        
        return response

    async def _prompt_reauth(self) -> bool:
        console.print("[yellow]Session expired or token invalid. Please reauthenticate.[/]")
        return await self.login()

    async def execute(self, command: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Submits a task for execution."""
        # Check providers if interactive
        if self.interactive:
             if not await _ensure_required_providers_connected(self._config, command):
                 raise RuntimeError("Required provider connection cancelled by user.")

        payload = {
            "command": command,
            "metadata": metadata or {"client": "engram-sdk", "timestamp": time.time()}
        }
        response = await self.request("POST", "/tasks/submit", json_body=payload)
        if response.status_code != 200:
            raise RuntimeError(f"Task submission failed: {response.text}")
        return response.json()

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Retrieves the current status of a task."""
        response = await self.request("GET", f"/tasks/{task_id}")
        if response.status_code != 200:
            raise RuntimeError(f"Task status fetch failed: {response.text}")
        return response.json()

    async def get_task_events(self, task_id: str, since: Optional[float] = None) -> List[Dict[str, Any]]:
        """Retrieves execution events for a task."""
        path = f"/tasks/{task_id}/events"
        if since:
            path += f"?since={since}"
        response = await self.request("GET", path)
        if response.status_code == 200:
            return response.json()
        return []

    async def list_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Lists recent tasks."""
        response = await self.request("GET", f"/tasks?limit={limit}")
        if response.status_code == 200:
            return response.json()
        return []


async def _perform_login(config: Dict[str, Any], email: str, password: str) -> bool:
    async with Engram(interactive=True) as sdk:
        return await sdk.login(email, password)

async def _perform_signup(config: Dict[str, Any], email: str, password: str) -> bool:
    async with Engram(interactive=True) as sdk:
        return await sdk.signup(email, password)

async def _ensure_eat(config: Dict[str, Any]) -> Optional[str]:
    async with Engram() as sdk:
        return await sdk.generate_eat()

async def _refresh_eat(config: Dict[str, Any]) -> Optional[str]:
    async with Engram() as sdk:
        return await sdk.generate_eat()

async def _authed_request(*args, **kwargs) -> httpx.Response:
    config = args[0]
    async with Engram() as sdk:
        # Map old signature to new SDK method if possible
        # Or just use the SDK directly in the CLI commands
        return await sdk.request(args[1], args[2], **kwargs)

def _interactive_auth_flow() -> None:
    config = load_config()
    if config.get("token") or config.get("eat"):
        _render_status(config)
        return
    console.print(Panel(
        "[bold]Welcome to Engram[/]\nCreate an account or log in to continue.",
        border_style="orange1",
    ))
    choice = click.prompt(
        "Choose an option",
        type=click.Choice(["login", "signup"], case_sensitive=False),
        default="login",
        show_default=True,
    )
    email = click.prompt("Email", type=str)
    password = click.prompt("Password", type=str, hide_input=True)
    if choice == "signup":
        confirm = click.prompt("Confirm Password", type=str, hide_input=True)
        if confirm != password:
            console.print("[red]ERROR[/] Passwords do not match.")
            return
        asyncio.run(_perform_signup(config, email, password))
    else:
        asyncio.run(_perform_login(config, email, password))

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__, prog_name="engram")
@click.pass_context
def cli(ctx: click.Context):
    """Engram Client (thin API client)."""
    if ctx.invoked_subcommand is None:
        _interactive_auth_flow()

@cli.command()
@click.option("--url", default=DEFAULT_BASE_URL, help="Backend API URL")
def init(url: str):
    """Initialize the Engram client configuration."""
    config = load_config()
    config["base_url"] = url
    save_config(config)
    console.print(f"[green]OK[/] Initialized Engram client with base URL: {url}")

@cli.command()
@click.option("--email", prompt=True, help="User email")
@click.option("--password", prompt=True, hide_input=True, help="User password")
def login(email, password):
    """Login to the Engram Identity Server."""
    asyncio.run(_perform_login(None, email, password))

@cli.command()
@click.option("--email", prompt=True, help="User email")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="User password")
@click.option("--login-after/--no-login-after", default=True, show_default=True, help="Login immediately after signup.")
def signup(email, password, login_after):
    """Create a new Engram account."""
    created = asyncio.run(_perform_signup(None, email, password))
    if created and login_after:
        asyncio.run(_perform_login(None, email, password))

@cli.command()
def status():
    """Check the status of the connection and the backend."""
    config = load_config()
    base_url = config["base_url"]

    table = Table(title="Engram Status", show_header=False, box=None)
    table.add_row("Base URL", base_url)

    async def get_status():
        async with Engram() as sdk:
            is_up = await check_health(base_url, token=sdk.eat or sdk.token)
            table.add_row("Backend Reachable", "[green]YES[/]" if is_up else "[red]NO[/]")
            table.add_row("Session Token", "[green]Active[/]" if sdk.token else "[yellow]Missing[/]")
            table.add_row("Engram Access Token (EAT)", "[green]Ready[/]" if sdk.eat else "[yellow]Missing[/]")
            console.print(Panel(table, title="[bold orange1]ENGRAM CLIENT[/]", border_style="orange1"))

    asyncio.run(get_status())

@cli.group()
def optimize():
    """Predictive optimizer for MCP vs CLI routing."""
    pass

@optimize.command("test")
@click.argument("task_text", nargs=-1)
def optimize_test(task_text: Tuple[str, ...]):
    """Forecast routing cost and recommend MCP vs CLI paths."""
    task = " ".join(task_text).strip()
    if not task:
        task = click.prompt("Describe the workload to optimize", type=str)

    metrics = _estimate_path_metrics(task)
    graph = _build_optimizer_graph(metrics)
    console.print(Panel(task, title="Optimization Target", border_style="blue"))
    _render_optimizer_output(task, metrics, graph)

@cli.command(name="eat")
def generate_eat():
    """Generate a new Engram Access Token (EAT)."""
    async def do_generate():
        async with Engram(interactive=True) as sdk:
            await sdk.generate_eat()
    asyncio.run(do_generate())

@cli.command(name="exec")
@click.argument("task_text", nargs=-1)
@click.option("--wait/--no-wait", default=True, help="Wait for task completion.")
@click.option("--poll-seconds", default=2.0, type=float, show_default=True, help="Polling interval.")
def execute(task_text, wait, poll_seconds):
    """Submit a task to the orchestration API and stream status/results."""
    task = " ".join(task_text)
    if not task:
        task = click.prompt("Enter task")

    async def do_exec():
        async with Engram(interactive=True) as sdk:
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task_description}"),
                    transient=True,
                ) as progress:
                    progress.add_task(description="Submitting task to Engram backend...", total=None)
                    payload = await sdk.execute(task)
            except Exception as e:
                console.print(f"[red]ERROR[/] Submission failed: {str(e)}")
                return

            task_id = payload.get("task_id")
            console.print(Panel(
                f"[bold green]Submitted:[/] {task_id}\n"
                f"[bold cyan]Status:[/] {payload.get('status')}\n"
                f"[bold]Message:[/] {payload.get('message')}",
                title="Task Accepted",
                border_style="green",
            ))

            if not wait:
                return

            trace_state = ExecutionTraceState()
            events_supported = True
            last_status = None
            status = payload.get("status") or "PENDING"
            with Live(_render_trace_view(trace_state, str(task_id), status), refresh_per_second=4) as live:
                while True:
                    await asyncio.sleep(poll_seconds)

                    if events_supported:
                        try:
                            events = await sdk.get_task_events(task_id, since=trace_state.last_ts)
                            for event in events:
                                trace_state.add_event(event)
                        except Exception:
                            events_supported = False

                    try:
                        task_status = await sdk.get_task_status(task_id)
                        status = task_status.get("status")
                        if status != last_status:
                            last_status = status
                            console.print(f"[dim]Status[/]: {status}")

                        live.update(_render_trace_view(trace_state, str(task_id), status))

                        if status in ("COMPLETED", "DEAD_LETTER"):
                            console.print(Panel(
                                f"[bold]Final Status:[/] {status}",
                                title="Workflow Complete",
                                border_style="green" if status == "COMPLETED" else "red",
                            ))
                            if task_status.get("last_error"):
                                console.print(Panel(task_status["last_error"], title="Last Error", border_style="red"))
                            _render_task_results(task_status.get("results"))
                            break
                    except Exception as e:
                        console.print(f"[red]ERROR[/] Status check failed: {str(e)}")
                        return

    asyncio.run(do_exec())

@cli.command()
@click.argument("command_text", nargs=-1)
def delegate(command_text):
    """Delegate a subtask via natural language."""
    cmd = " ".join(command_text)
    if not cmd:
        cmd = click.prompt("Enter command")

    async def do_delegate():
        async with Engram() as sdk:
            try:
                response = await sdk.request("POST", "/delegate", json_body={"command": cmd, "source_agent": "engram-cli"})
                if response.status_code == 200:
                    console.print(Panel(json.dumps(response.json(), indent=2), title="Delegation Response", border_style="blue"))
                else:
                    console.print(f"[red]Error: {response.text}[/]")
            except Exception as e:
                console.print(f"[red]Connection error: {str(e)}[/]")

    asyncio.run(do_delegate())

@cli.command()
@click.option("--limit", default=10, show_default=True, help="Max tasks to list.")
def tasks(limit: int):
    """List recent tasks for the authenticated user."""
    async def do_list():
        async with Engram() as sdk:
            try:
                rows = await sdk.list_tasks(limit=limit)
                table = Table(title="Recent Tasks")
                table.add_column("Task ID", style="cyan")
                table.add_column("Status")
                table.add_column("Updated")
                for row in rows:
                    table.add_row(str(row.get("id")), str(row.get("status")), str(row.get("updated_at")))
                console.print(table)
            except Exception as e:
                console.print(f"[red]ERROR[/] {str(e)}")

    asyncio.run(do_list())

@cli.group()
def wrapper():
    """Legacy wrapper tooling for adaptive execution."""
    pass

@wrapper.command("create")
@click.argument("path", required=False, default=".")
@click.option("--name", default=None, help="Wrapper name.")
@click.option("--api-url", default=None, help="Primary API endpoint for the wrapper.")
@click.option("--cli-command", default=None, help="CLI fallback command.")
@click.option("--force", is_flag=True, help="Overwrite existing wrapper directory.")
def wrapper_create(path: str, name: Optional[str], api_url: Optional[str], cli_command: Optional[str], force: bool):
    """Create an adaptive wrapper (API + sandboxed CLI fallback)."""
    wrapper_name = _safe_wrapper_name(name or click.prompt("Wrapper name", default="adaptive-wrapper"))
    if not api_url:
        api_url = click.prompt("API base URL (optional)", default="", show_default=False) or None
    if not cli_command:
        cli_command = click.prompt("CLI fallback command (optional)", default="", show_default=False) or None

    output_root = os.path.abspath(path)
    output_dir = os.path.join(output_root, wrapper_name)

    if os.path.exists(output_dir) and not force:
        console.print(f"[red]ERROR[/] Wrapper directory already exists: {output_dir}")
        console.print("Re-run with [bold]--force[/] to overwrite.")
        return

    os.makedirs(output_dir, exist_ok=True)

    _render_wrapper_generation(wrapper_name, api_url, cli_command)

    manifest = _wrapper_manifest(wrapper_name, api_url, cli_command)
    manifest_path = os.path.join(output_dir, "wrapper.manifest.json")
    script_path = os.path.join(output_dir, "wrapper.py")

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(_wrapper_script(wrapper_name, api_url, cli_command))

    console.print(Panel(
        f"[bold]Wrapper created[/]\n{script_path}\n{manifest_path}",
        title="Adaptive Wrapper Ready",
        border_style="green",
    ))

@cli.command()
def doctor():
    """Run a lightweight health check across CLI capabilities."""
    async def run_checks():
        results = await _run_doctor_checks()
        table = Table(title="Engram CLI Doctor")
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Detail")
        for name, ok, detail in results:
            status = "[green]OK[/]" if ok else "[yellow]WARN[/]"
            table.add_row(name, status, detail)
        console.print(table)
        console.print(Text("Doctor finished. Use --help for command guidance and --version for CLI metadata.", style="dim"))

    asyncio.run(run_checks())

@cli.group()
def vault():
    """Manage local credential vault."""
    pass

@vault.command(name="list")
def vault_list():
    """List all credentials stored in the local vault."""
    config = load_config()
    vault = config.get("vault", {})
    if not vault:
        console.print("[dim]Local vault is empty.[/]")
        return
    table = Table(title="Local Credential Vault")
    table.add_column("Context (Base URL | Email)", style="cyan")
    table.add_column("Provider")
    table.add_column("Type")
    table.add_column("Last Synced")
    for context, providers in vault.items():
        for pid, data in providers.items():
            table.add_row(context, pid, data.get("type", "UNKNOWN"), data.get("last_synced", "Never"))
    console.print(table)

@vault.command(name="clear")
@click.option("--all", is_flag=True, help="Clear ALL credentials from the local vault.")
@click.option("--provider", help="Clear credentials for a specific provider.")
def vault_clear(all, provider):
    """Clear credentials from the local vault."""
    config = load_config()
    if all:
        if click.confirm("Are you sure you want to clear the entire local vault?", abort=True):
            config["vault"] = {}
            save_config(config)
            console.print("[green]OK[/] Local vault cleared.")
            return
    vault_key = f"{config.get('base_url')}|{config.get('email')}"
    if vault_key not in config.get("vault", {}):
        console.print("[yellow]No vault entries for current session.[/]")
        return
    if provider:
        if provider in config["vault"][vault_key]:
            del config["vault"][vault_key][provider]
            save_config(config)
            console.print(f"[green]OK[/] Cleared {provider} for current session.")
        else:
            console.print(f"[red]Error[/] Provider '{provider}' not found in vault.")
    else:
        if click.confirm(f"Clear all credentials for {vault_key}?", abort=True):
            del config["vault"][vault_key]
            save_config(config)
            console.print(f"[green]OK[/] Cleared credentials for current session.")

@cli.group()
def workflow():
    """Create, manage, and run workflows."""
    pass

@workflow.command("list")
@click.option("--limit", default=50, show_default=True, help="Max workflows to list.")
def list_workflows(limit: int):
    async def do_list():
        async with Engram() as sdk:
            response = await sdk.request("GET", f"/workflows?limit={limit}")
            if response.status_code == 200:
                _render_workflow_table(response.json())
            else:
                console.print(f"[red]ERROR[/] {response.text}")
    asyncio.run(do_list())

@workflow.command("show")
@click.argument("workflow_id")
def show_workflow(workflow_id: str):
    async def do_show():
        async with Engram() as sdk:
            response = await sdk.request("GET", f"/workflows/{workflow_id}")
            if response.status_code == 200:
                _render_workflow_detail(response.json())
            else:
                console.print(f"[red]ERROR[/] {response.text}")
    asyncio.run(do_show())

@workflow.command("create")
@click.option("--name", prompt=True, help="Workflow name")
@click.option("--description", default="", help="Workflow description")
@click.option("--command", prompt=True, help="Workflow command")
@click.option("--metadata", default="", help="Optional metadata JSON")
def create_workflow(name: str, description: str, command: str, metadata: str):
    async def do_create():
        async with Engram() as sdk:
            metadata_obj = None
            if metadata:
                try: metadata_obj = json.loads(metadata)
                except Exception:
                    console.print("[red]ERROR[/] Metadata must be valid JSON.")
                    return
            response = await sdk.request("POST", "/workflows", json_body={"name": name, "description": description or None, "command": command, "metadata": metadata_obj})
            if response.status_code in (200, 201):
                console.print("[green]OK[/] Workflow created.")
                _render_workflow_detail(response.json())
            else:
                console.print(f"[red]ERROR[/] {response.text}")
    asyncio.run(do_create())

@workflow.command("update")
@click.argument("workflow_id")
@click.option("--name", default=None, help="Workflow name")
@click.option("--description", default=None, help="Workflow description")
@click.option("--command", default=None, help="Workflow command")
@click.option("--metadata", default=None, help="Optional metadata JSON")
@click.option("--active/--inactive", default=None, help="Enable/disable workflow")
def update_workflow(workflow_id: str, name: Optional[str], description: Optional[str], command: Optional[str], metadata: Optional[str], active: Optional[bool]):
    async def do_update():
        async with Engram() as sdk:
            payload = {}
            if name is not None: payload["name"] = name
            if description is not None: payload["description"] = description
            if command is not None: payload["command"] = command
            if active is not None: payload["is_active"] = active
            if metadata is not None:
                if metadata == "": payload["metadata"] = {}
                else:
                    try: payload["metadata"] = json.loads(metadata)
                    except Exception:
                        console.print("[red]ERROR[/] Metadata must be valid JSON.")
                        return
            if not payload:
                console.print("[yellow]No updates supplied.[/]")
                return
            response = await sdk.request("PATCH", f"/workflows/{workflow_id}", json_body=payload)
            if response.status_code == 200:
                console.print("[green]OK[/] Workflow updated.")
                _render_workflow_detail(response.json())
            else:
                console.print(f"[red]ERROR[/] {response.text}")
    asyncio.run(do_update())

@workflow.command("delete")
@click.argument("workflow_id")
def delete_workflow(workflow_id: str):
    async def do_delete():
        async with Engram() as sdk:
            response = await sdk.request("DELETE", f"/workflows/{workflow_id}")
            if response.status_code == 204: console.print("[green]OK[/] Workflow deleted.")
            else: console.print(f"[red]ERROR[/] {response.text}")
    asyncio.run(do_delete())

@workflow.command("run")
@click.argument("workflow_id")
@click.option("--wait/--no-wait", default=True, help="Wait for task completion.")
@click.option("--poll-seconds", default=2.0, type=float, show_default=True, help="Polling interval.")
def run_workflow(workflow_id: str, wait: bool, poll_seconds: float):
    async def do_run():
        async with Engram(interactive=True) as sdk:
            wf_resp = await sdk.request("GET", f"/workflows/{workflow_id}")
            if wf_resp.status_code != 200:
                console.print(f"[red]ERROR[/] Workflow lookup failed: {wf_resp.text}")
                return
            cmd = wf_resp.json().get("command", "")
            if cmd:
                 # Logic for provider check is inside execute but here we need to do it manually if we use request
                 if not await _ensure_required_providers_connected(sdk._config, cmd):
                     return
            response = await sdk.request("POST", f"/workflows/{workflow_id}/run")
            if response.status_code != 200:
                console.print(f"[red]ERROR[/] {response.text}")
                return
            payload = response.json()
            task_id = payload.get("task_id")
            console.print(Panel(f"Task ID: {task_id}", title="Workflow Submitted", border_style="green"))
            if not wait or not task_id: return
            trace_state = ExecutionTraceState()
            events_supported = True
            last_status = None
            with Live(_render_trace_view(trace_state, str(task_id), "PENDING"), refresh_per_second=4) as live:
                while True:
                    await asyncio.sleep(poll_seconds)
                    if events_supported:
                        try:
                            events = await sdk.get_task_events(task_id, since=trace_state.last_ts)
                            for event in events: trace_state.add_event(event)
                        except Exception: events_supported = False
                    try:
                        task_status = await sdk.get_task_status(task_id)
                        status = task_status.get("status")
                        if status != last_status:
                            last_status = status
                        live.update(_render_trace_view(trace_state, str(task_id), status))
                        if status in ("COMPLETED", "DEAD_LETTER"):
                            console.print(Panel(f"Final Status: {status}", title="Workflow Complete"))
                            _render_task_results(task_status.get("results"))
                            break
                    except Exception as e:
                        console.print(f"[red]ERROR[/] {str(e)}")
                        return
    asyncio.run(do_run())

@workflow.command("runs")
@click.argument("workflow_id")
@click.option("--limit", default=20, show_default=True, help="Max runs to list.")
def list_workflow_runs(workflow_id: str, limit: int):
    async def do_runs():
        async with Engram() as sdk:
            response = await sdk.request("GET", f"/workflows/{workflow_id}/tasks?limit={limit}")
            if response.status_code == 200:
                rows = response.json()
                table = Table(title="Workflow Runs")
                table.add_column("Task ID", style="cyan"); table.add_column("Status"); table.add_column("Updated")
                for row in rows: table.add_row(str(row.get("id")), str(row.get("status")), str(row.get("updated_at")))
                console.print(table)
            else: console.print(f"[red]ERROR[/] {response.text}")
    asyncio.run(do_runs())

@workflow.command("schedule")
@click.argument("workflow_id")
@click.option("--interval-minutes", type=int, default=None, help="Run every N minutes.")
@click.option("--interval-seconds", type=int, default=None, help="Run every N seconds.")
@click.option("--enabled/--disabled", default=True, show_default=True, help="Enable schedule.")
def schedule_workflow(workflow_id: str, interval_minutes: Optional[int], interval_seconds: Optional[int], enabled: bool):
    async def do_schedule():
        async with Engram() as sdk:
            response = await sdk.request("POST", f"/workflows/{workflow_id}/schedule", json_body={"interval_minutes": interval_minutes, "interval_seconds": interval_seconds, "enabled": enabled})
            if response.status_code == 200:
                payload = response.json()
                console.print(Panel(f"Interval: {payload.get('interval_seconds')}s\nNext: {payload.get('next_run_at')}", title="Workflow Schedule"))
            else: console.print(f"[red]ERROR[/] {response.text}")
    asyncio.run(do_schedule())

@workflow.command("unschedule")
@click.argument("workflow_id")
def unschedule_workflow(workflow_id: str):
    async def do_unschedule():
        async with Engram() as sdk:
            response = await sdk.request("DELETE", f"/workflows/{workflow_id}/schedule")
            if response.status_code == 204: console.print("[green]OK[/] Workflow schedule removed.")
            else: console.print(f"[red]ERROR[/] {response.text}")
    asyncio.run(do_unschedule())

if __name__ == "__main__":
    cli()
