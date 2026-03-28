import os
import json
import click
import httpx
import asyncio
import time
from typing import Optional, Dict, Any, List
from collections import deque
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.live import Live
from cryptography.fernet import Fernet, InvalidToken

console = Console()

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

async def _request(
    method: str,
    base_url: str,
    path: str,
    *,
    json_body: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 60.0,
) -> httpx.Response:
    url = f"{base_url}{path}"
    async with httpx.AsyncClient(timeout=timeout) as client:
        return await client.request(method, url, json=json_body, data=data, headers=headers)

async def _ensure_eat(config: Dict[str, Any]) -> Optional[str]:
    if config.get("eat"):
        return config["eat"]
    token = config.get("token")
    if not token:
        return None
    resp = await _request(
        "POST",
        config["base_url"],
        "/auth/tokens/generate-eat",
        headers=_auth_header(token),
    )
    if resp.status_code == 200:
        eat = resp.json().get("eat")
        config["eat"] = eat
        save_config(config)
        return eat
    return None

async def _refresh_eat(config: Dict[str, Any]) -> Optional[str]:
    token = config.get("token")
    if not token:
        return None
    resp = await _request(
        "POST",
        config["base_url"],
        "/auth/tokens/generate-eat",
        headers=_auth_header(token),
    )
    if resp.status_code == 200:
        eat = resp.json().get("eat")
        config["eat"] = eat
        save_config(config)
        return eat
    return None

async def _prompt_reauth(config: Dict[str, Any]) -> bool:
    console.print("[yellow]Session expired or token invalid. Please reauthenticate.[/]")
    email_default = config.get("email") or ""
    email = click.prompt("Email", type=str, default=email_default, show_default=bool(email_default))
    password = click.prompt("Password", type=str, hide_input=True)
    ok = await _perform_login(config, email, password)
    return ok

async def _authed_request(
    config: Dict[str, Any],
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
    token = None
    if use_session_token:
        token = config.get("token")
        if not token:
            if await _prompt_reauth(config):
                token = config.get("token")
    else:
        token = config.get("eat") or await _ensure_eat(config)
        if not token:
            if await _prompt_reauth(config):
                token = config.get("eat") or await _ensure_eat(config)

    auth_headers = _auth_header(token)
    request_headers = _merge_headers(headers, auth_headers)
    response = await _request(
        method,
        config["base_url"],
        path,
        json_body=json_body,
        data=data,
        headers=request_headers,
        timeout=timeout,
    )

    if allow_retry and _response_indicates_token_issue(response):
        refreshed: Optional[str] = None
        if not use_session_token:
            refreshed = await _refresh_eat(config)
        if not refreshed:
            if await _prompt_reauth(config):
                refreshed = config.get("eat") or await _ensure_eat(config)
        if refreshed or (use_session_token and config.get("token")):
            retry_token = config.get("token") if use_session_token else refreshed
            retry_headers = _merge_headers(headers, _auth_header(retry_token))
            return await _request(
                method,
                config["base_url"],
                path,
                json_body=json_body,
                data=data,
                headers=retry_headers,
                timeout=timeout,
            )
    return response

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
    response = await _authed_request(config, "GET", "/credentials")
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
    
    response = await _authed_request(config, "POST", "/credentials", json_body=payload)
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

    response = await _authed_request(config, "POST", "/credentials", json_body=payload)
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

async def _perform_login(config: Dict[str, Any], email: str, password: str) -> bool:
    base_url = config["base_url"]
    try:
        response = await _request(
            "POST",
            base_url,
            "/auth/login",
            data={"username": email, "password": password},
            headers=_auth_header(config.get("eat")),
        )
        if response.status_code == 200:
            data = response.json()
            config["token"] = data["access_token"]
            config["email"] = email
            save_config(config)
            console.print("[green]OK[/] Login successful.")

            console.print("[dim]Generating Engram Access Token (EAT)...[/]")
            eat_resp = await _request(
                "POST",
                base_url,
                "/auth/tokens/generate-eat",
                headers=_auth_header(data["access_token"]),
            )
            if eat_resp.status_code == 200:
                config["eat"] = eat_resp.json()["eat"]
                save_config(config)
                console.print("[green]OK[/] EAT generated and stored.")
            else:
                console.print(f"[yellow]WARN[/] EAT not generated: {eat_resp.text}")
            return True
        console.print(f"[red]ERROR[/] Login failed: {response.text}")
        return False
    except Exception as exc:
        console.print(f"[red]ERROR[/] Connection error: {str(exc)}")
        return False

async def _perform_signup(config: Dict[str, Any], email: str, password: str) -> bool:
    base_url = config["base_url"]
    try:
        response = await _request(
            "POST",
            base_url,
            "/auth/signup",
            json_body={"email": email, "password": password, "user_metadata": {"source": "cli_client"}},
            headers=_auth_header(config.get("eat")),
        )
        if response.status_code == 201:
            console.print("[green]OK[/] Account created successfully.")
            return True
        console.print(f"[red]ERROR[/] Signup failed: {response.text}")
        return False
    except Exception as exc:
        console.print(f"[red]ERROR[/] Connection error: {str(exc)}")
        return False

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
        created = asyncio.run(_perform_signup(config, email, password))
        if not created:
            return
    asyncio.run(_perform_login(config, email, password))

@click.group(invoke_without_command=True)
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
    config = load_config()
    asyncio.run(_perform_login(config, email, password))

@cli.command()
@click.option("--email", prompt=True, help="User email")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="User password")
@click.option("--login-after/--no-login-after", default=True, show_default=True, help="Login immediately after signup.")
def signup(email, password, login_after):
    """Create a new Engram account."""
    config = load_config()
    created = asyncio.run(_perform_signup(config, email, password))
    if created and login_after:
        asyncio.run(_perform_login(config, email, password))

@cli.command()
def status():
    """Check the status of the connection and the backend."""
    config = load_config()
    base_url = config["base_url"]

    table = Table(title="Engram Status", show_header=False, box=None)
    table.add_row("Base URL", base_url)

    async def get_status():
        token = config.get("eat") or config.get("token")
        is_up = await check_health(base_url, token=token)
        table.add_row("Backend Reachable", "[green]YES[/]" if is_up else "[red]NO[/]")
        table.add_row("Session Token", "[green]Active[/]" if config.get("token") else "[yellow]Missing[/]")
        table.add_row("Engram Access Token (EAT)", "[green]Ready[/]" if config.get("eat") else "[yellow]Missing[/]")
        console.print(Panel(table, title="[bold orange1]ENGRAM CLIENT[/]", border_style="orange1"))

    asyncio.run(get_status())

@cli.command(name="eat")
def generate_eat():
    """Generate a new Engram Access Token (EAT)."""
    config = load_config()
    base_url = config["base_url"]
    token = config.get("token")
    if not token:
        console.print("[yellow]Session token missing. Prompting for login...[/]")
        if not asyncio.run(_prompt_reauth(config)):
            console.print("[red]ERROR[/] Login required to generate EAT.")
            return

    async def do_generate():
        try:
            response = await _authed_request(
                config,
                "POST",
                "/auth/tokens/generate-eat",
                use_session_token=True,
            )
            if response.status_code == 200:
                config["eat"] = response.json()["eat"]
                save_config(config)
                console.print("[green]OK[/] EAT generated and stored.")
            else:
                console.print(f"[red]ERROR[/] EAT generation failed: {response.text}")
        except Exception as e:
            console.print(f"[red]ERROR[/] Connection error: {str(e)}")

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

    config = load_config()
    base_url = config["base_url"]

    async def do_exec():
        request_body = {
            "command": task,
            "metadata": {
                "client": "engram-cli",
                "timestamp": time.time(),
            },
        }

        if not await _ensure_required_providers_connected(config, task):
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task_description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Submitting task to Engram backend...", total=None)
            try:
                response = await _authed_request(
                    config,
                    "POST",
                    "/tasks/submit",
                    json_body=request_body,
                )
            except Exception as e:
                console.print(f"[red]ERROR[/] Submission failed: {str(e)}")
                return

        if response.status_code != 200:
            console.print(Panel(
                f"[red]Error {response.status_code}: {response.text}[/]",
                title="Submission Failed",
                border_style="red",
            ))
            return

        payload = response.json()
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

                # Fetch execution events (if supported)
                if events_supported:
                    events_path = f"/tasks/{task_id}/events"
                    if trace_state.last_ts:
                        events_path += f"?since={trace_state.last_ts}"
                    events_resp = await _authed_request(
                        config,
                        "GET",
                        events_path,
                        timeout=30.0,
                        allow_retry=False,
                    )
                    if events_resp.status_code == 200:
                        for event in events_resp.json():
                            trace_state.add_event(event)
                    elif events_resp.status_code in (404, 422):
                        events_supported = False
                    else:
                        console.print(f"[yellow]WARN[/] Event stream unavailable: {events_resp.text}")

                status_resp = await _authed_request(
                    config,
                    "GET",
                    f"/tasks/{task_id}",
                )
                if status_resp.status_code != 200:
                    console.print(f"[red]ERROR[/] Status check failed: {status_resp.text}")
                    return
                task_status = status_resp.json()
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
                        console.print(Panel(
                            task_status["last_error"],
                            title="Last Error",
                            border_style="red",
                        ))
                    _render_task_results(task_status.get("results"))
                    break

    asyncio.run(do_exec())

@cli.command()
@click.argument("command_text", nargs=-1)
def delegate(command_text):
    """Delegate a subtask via natural language."""
    cmd = " ".join(command_text)
    if not cmd:
        cmd = click.prompt("Enter command")

    config = load_config()
    base_url = config["base_url"]

    async def do_delegate():
        try:
            response = await _authed_request(
                config,
                "POST",
                "/delegate",
                json_body={"command": cmd, "source_agent": "engram-cli"},
            )
            if response.status_code == 200:
                result = response.json()
                console.print(Panel(
                    f"[bold]Delegation Result:[/]\n{json.dumps(result, indent=2)}",
                    title="Delegation Response",
                    border_style="blue",
                ))
            else:
                console.print(f"[red]Error: {response.text}[/]")
        except Exception as e:
            console.print(f"[red]Connection error: {str(e)}[/]")

    asyncio.run(do_delegate())

@cli.command()
@click.option("--limit", default=10, show_default=True, help="Max tasks to list.")
def tasks(limit: int):
    """List recent tasks for the authenticated user."""
    config = load_config()
    base_url = config["base_url"]

    async def do_list():
        response = await _authed_request(
            config,
            "GET",
            "/tasks",
            timeout=30.0,
        )
        if response.status_code != 200:
            console.print(f"[red]ERROR[/] {response.text}")
            return
        rows: List[Dict[str, Any]] = response.json()
        table = Table(title="Recent Tasks")
        table.add_column("Task ID", style="cyan")
        table.add_column("Status")
        table.add_column("Updated")
        for row in rows[:limit]:
            table.add_row(
                str(row.get("id")),
                str(row.get("status")),
                str(row.get("updated_at")),
            )
        console.print(table)

    asyncio.run(do_list())

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
            table.add_row(
                context,
                pid,
                data.get("type", "UNKNOWN"),
                data.get("last_synced", "Never")
            )
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
    config = load_config()

    async def do_list():
        response = await _authed_request(
            config,
            "GET",
            f"/workflows?limit={limit}",
        )
        if response.status_code != 200:
            console.print(f"[red]ERROR[/] {response.text}")
            return
        _render_workflow_table(response.json())

    asyncio.run(do_list())

@workflow.command("show")
@click.argument("workflow_id")
def show_workflow(workflow_id: str):
    config = load_config()

    async def do_show():
        response = await _authed_request(
            config,
            "GET",
            f"/workflows/{workflow_id}",
        )
        if response.status_code != 200:
            console.print(f"[red]ERROR[/] {response.text}")
            return
        _render_workflow_detail(response.json())

    asyncio.run(do_show())

@workflow.command("create")
@click.option("--name", prompt=True, help="Workflow name")
@click.option("--description", default="", help="Workflow description")
@click.option("--command", prompt=True, help="Workflow command")
@click.option("--metadata", default="", help="Optional metadata JSON")
def create_workflow(name: str, description: str, command: str, metadata: str):
    config = load_config()

    async def do_create():
        metadata_obj = None
        if metadata:
            try:
                metadata_obj = json.loads(metadata)
            except Exception:
                console.print("[red]ERROR[/] Metadata must be valid JSON.")
                return
        response = await _authed_request(
            config,
            "POST",
            "/workflows",
            json_body={
                "name": name,
                "description": description or None,
                "command": command,
                "metadata": metadata_obj,
            },
        )
        if response.status_code not in (200, 201):
            console.print(f"[red]ERROR[/] {response.text}")
            return
        console.print("[green]OK[/] Workflow created.")
        _render_workflow_detail(response.json())

    asyncio.run(do_create())

@workflow.command("update")
@click.argument("workflow_id")
@click.option("--name", default=None, help="Workflow name")
@click.option("--description", default=None, help="Workflow description")
@click.option("--command", default=None, help="Workflow command")
@click.option("--metadata", default=None, help="Optional metadata JSON")
@click.option("--active/--inactive", default=None, help="Enable/disable workflow")
def update_workflow(workflow_id: str, name: Optional[str], description: Optional[str], command: Optional[str], metadata: Optional[str], active: Optional[bool]):
    config = load_config()

    async def do_update():
        metadata_obj = None
        if metadata is not None:
            if metadata == "":
                metadata_obj = {}
            else:
                try:
                    metadata_obj = json.loads(metadata)
                except Exception:
                    console.print("[red]ERROR[/] Metadata must be valid JSON.")
                    return
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if command is not None:
            payload["command"] = command
        if metadata is not None:
            payload["metadata"] = metadata_obj
        if active is not None:
            payload["is_active"] = active
        if not payload:
            console.print("[yellow]No updates supplied.[/]")
            return
        response = await _authed_request(
            config,
            "PATCH",
            f"/workflows/{workflow_id}",
            json_body=payload,
        )
        if response.status_code != 200:
            console.print(f"[red]ERROR[/] {response.text}")
            return
        console.print("[green]OK[/] Workflow updated.")
        _render_workflow_detail(response.json())

    asyncio.run(do_update())

@workflow.command("delete")
@click.argument("workflow_id")
def delete_workflow(workflow_id: str):
    config = load_config()

    async def do_delete():
        response = await _authed_request(
            config,
            "DELETE",
            f"/workflows/{workflow_id}",
        )
        if response.status_code != 204:
            console.print(f"[red]ERROR[/] {response.text}")
            return
        console.print("[green]OK[/] Workflow deleted.")

    asyncio.run(do_delete())

@workflow.command("run")
@click.argument("workflow_id")
@click.option("--wait/--no-wait", default=True, help="Wait for task completion.")
@click.option("--poll-seconds", default=2.0, type=float, show_default=True, help="Polling interval.")
def run_workflow(workflow_id: str, wait: bool, poll_seconds: float):
    config = load_config()

    async def do_run():
        workflow_resp = await _authed_request(
            config,
            "GET",
            f"/workflows/{workflow_id}",
        )
        if workflow_resp.status_code != 200:
            console.print(f"[red]ERROR[/] Workflow lookup failed: {workflow_resp.text}")
            return
        workflow_command = workflow_resp.json().get("command", "")
        if workflow_command:
            if not await _ensure_required_providers_connected(config, workflow_command):
                return
        response = await _authed_request(
            config,
            "POST",
            f"/workflows/{workflow_id}/run",
        )
        if response.status_code != 200:
            console.print(f"[red]ERROR[/] {response.text}")
            return
        payload = response.json()
        task_id = payload.get("task_id")
        console.print(Panel(
            f"[bold green]Workflow queued:[/] {workflow_id}\n"
            f"[bold cyan]Task ID:[/] {task_id}\n"
            f"[bold]Status:[/] {payload.get('status')}",
            title="Workflow Submitted",
            border_style="green",
        ))

        if not wait or not task_id:
            return

        trace_state = ExecutionTraceState()
        events_supported = True
        last_status = None
        status = payload.get("status") or "PENDING"
        with Live(_render_trace_view(trace_state, str(task_id), status), refresh_per_second=4) as live:
            while True:
                await asyncio.sleep(poll_seconds)

                if events_supported:
                    events_path = f"/tasks/{task_id}/events"
                    if trace_state.last_ts:
                        events_path += f"?since={trace_state.last_ts}"
                    events_resp = await _authed_request(
                        config,
                        "GET",
                        events_path,
                        timeout=30.0,
                        allow_retry=False,
                    )
                    if events_resp.status_code == 200:
                        for event in events_resp.json():
                            trace_state.add_event(event)
                    elif events_resp.status_code in (404, 422):
                        events_supported = False
                    else:
                        console.print(f"[yellow]WARN[/] Event stream unavailable: {events_resp.text}")

                status_resp = await _authed_request(
                    config,
                    "GET",
                    f"/tasks/{task_id}",
                )
                if status_resp.status_code != 200:
                    console.print(f"[red]ERROR[/] Status check failed: {status_resp.text}")
                    return
                task_status = status_resp.json()
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
                        console.print(Panel(
                            task_status["last_error"],
                            title="Last Error",
                            border_style="red",
                        ))
                    _render_task_results(task_status.get("results"))
                    break

    asyncio.run(do_run())

@workflow.command("runs")
@click.argument("workflow_id")
@click.option("--limit", default=20, show_default=True, help="Max runs to list.")
def list_workflow_runs(workflow_id: str, limit: int):
    config = load_config()

    async def do_runs():
        response = await _authed_request(
            config,
            "GET",
            f"/workflows/{workflow_id}/tasks?limit={limit}",
        )
        if response.status_code != 200:
            console.print(f"[red]ERROR[/] {response.text}")
            return
        rows = response.json()
        table = Table(title="Workflow Runs")
        table.add_column("Task ID", style="cyan")
        table.add_column("Status")
        table.add_column("Updated")
        for row in rows:
            table.add_row(
                str(row.get("id")),
                str(row.get("status")),
                str(row.get("updated_at")),
            )
        console.print(table)

    asyncio.run(do_runs())

@workflow.command("schedule")
@click.argument("workflow_id")
@click.option("--interval-minutes", type=int, default=None, help="Run every N minutes.")
@click.option("--interval-seconds", type=int, default=None, help="Run every N seconds.")
@click.option("--enabled/--disabled", default=True, show_default=True, help="Enable schedule.")
def schedule_workflow(workflow_id: str, interval_minutes: Optional[int], interval_seconds: Optional[int], enabled: bool):
    config = load_config()

    async def do_schedule():
        response = await _authed_request(
            config,
            "POST",
            f"/workflows/{workflow_id}/schedule",
            json_body={
                "interval_minutes": interval_minutes,
                "interval_seconds": interval_seconds,
                "enabled": enabled,
            },
        )
        if response.status_code != 200:
            console.print(f"[red]ERROR[/] {response.text}")
            return
        payload = response.json()
        console.print(Panel(
            f"[bold]Interval (sec):[/] {payload.get('interval_seconds')}\n"
            f"[bold]Enabled:[/] {payload.get('enabled')}\n"
            f"[bold]Next Run:[/] {payload.get('next_run_at')}",
            title="Workflow Schedule",
            border_style="orange1",
        ))

    asyncio.run(do_schedule())

@workflow.command("unschedule")
@click.argument("workflow_id")
def unschedule_workflow(workflow_id: str):
    config = load_config()

    async def do_unschedule():
        response = await _authed_request(
            config,
            "DELETE",
            f"/workflows/{workflow_id}/schedule",
        )
        if response.status_code != 204:
            console.print(f"[red]ERROR[/] {response.text}")
            return
        console.print("[green]OK[/] Workflow schedule removed.")

    asyncio.run(do_unschedule())

if __name__ == "__main__":
    cli()
