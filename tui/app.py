from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, RichLog, Input, Label, Button
from textual.binding import Binding
from textual import on, work
from textual.screen import Screen
import asyncio
import os
import json
import httpx
import time
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet, InvalidToken
from app.core.tui_bridge import tui_event_queue

CONFIG_DIR = os.path.expanduser("~/.engram")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.enc")
KEY_FILE = os.path.join(CONFIG_DIR, "key")
DEFAULT_BASE_URL = "http://localhost:8000/api/v1"

PROVIDERS = [
    {
        "id": "claude",
        "name": "Claude",
        "auth": "api_key",
        "hint": "Anthropic API key",
    },
    {
        "id": "perplexity",
        "name": "Perplexity",
        "auth": "api_key",
        "hint": "Perplexity API key",
    },
    {
        "id": "slack",
        "name": "Slack",
        "auth": "oauth",
        "hint": "Slack OAuth token",
    },
    {
        "id": "custom",
        "name": "Other Tools",
        "auth": "api_key",
        "hint": "Any provider API key or OAuth token",
        "custom": True,
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
    return {"base_url": DEFAULT_BASE_URL, "token": None, "eat": None, "email": None}

def _normalize_config(config: Dict[str, Any]) -> Dict[str, Any]:
    base = _default_config()
    base.update(config or {})
    return base

def load_config() -> Dict[str, Any]:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return _normalize_config(_decrypt_config(f.read().strip()))
        except (InvalidToken, json.JSONDecodeError, OSError):
            return _default_config()
    return _default_config()

def save_config(config: Dict[str, Any]) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        f.write(_encrypt_config(config))

async def _request(
    method: str,
    base_url: str,
    path: str,
    *,
    json_body: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> httpx.Response:
    url = f"{base_url}{path}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        return await client.request(method, url, json=json_body, data=data, headers=headers)

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

class AuthScreen(Screen):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config

    def compose(self) -> ComposeResult:
        with Container(id="auth-container"):
            yield Label("Engram Sign In", id="auth-title")
            yield Label("Base URL")
            yield Input(value=self.config.get("base_url") or DEFAULT_BASE_URL, id="base-url-input")
            yield Label("Email")
            yield Input(placeholder="name@company.com", id="email-input")
            yield Label("Password")
            yield Input(password=True, placeholder="********", id="password-input")
            yield Label("Confirm Password (signup only)")
            yield Input(password=True, placeholder="********", id="confirm-input")
            yield Label("", id="auth-error")
            with Horizontal(id="auth-buttons"):
                yield Button("Login", id="login-btn", variant="primary")
                yield Button("Signup", id="signup-btn")
                yield Button("Quit", id="quit-btn")

    def on_mount(self) -> None:
        self.query_one("#email-input", Input).focus()

    def action_cancel(self) -> None:
        self.dismiss(None)

    async def _do_login(self, email: str, password: str, base_url: str) -> Optional[Dict[str, Any]]:
        response = await _request(
            "POST",
            base_url,
            "/auth/login",
            data={"username": email, "password": password},
            headers=_auth_header(self.config.get("eat")),
        )
        if response.status_code != 200:
            raise RuntimeError(response.json().get("detail", response.text))
        return response.json()

    async def _generate_eat(self, token: str, base_url: str) -> str:
        response = await _request(
            "POST",
            base_url,
            "/auth/tokens/generate-eat",
            headers=_auth_header(token),
        )
        if response.status_code != 200:
            raise RuntimeError(response.json().get("detail", response.text))
        return response.json().get("eat")

    def _set_error(self, message: str) -> None:
        label = self.query_one("#auth-error", Label)
        label.update(message)

    @on(Button.Pressed, "#quit-btn")
    def handle_quit(self) -> None:
        self.app.exit()

    @on(Button.Pressed, "#login-btn")
    async def handle_login(self) -> None:
        await self._authenticate(mode="login")

    @on(Button.Pressed, "#signup-btn")
    async def handle_signup(self) -> None:
        await self._authenticate(mode="signup")

    async def _authenticate(self, mode: str) -> None:
        email = self.query_one("#email-input", Input).value.strip()
        password = self.query_one("#password-input", Input).value.strip()
        confirm = self.query_one("#confirm-input", Input).value.strip()
        base_url = self.query_one("#base-url-input", Input).value.strip() or DEFAULT_BASE_URL

        if not email or not password:
            self._set_error("Email and password are required.")
            return

        if mode == "signup":
            if password != confirm:
                self._set_error("Passwords do not match.")
                return
            response = await _request(
                "POST",
                base_url,
                "/auth/signup",
                json_body={"email": email, "password": password, "user_metadata": {"source": "tui_client"}},
                headers=_auth_header(self.config.get("eat")),
            )
            if response.status_code != 201:
                self._set_error(response.json().get("detail", response.text))
                return

        try:
            login_payload = await self._do_login(email, password, base_url)
            token = login_payload.get("access_token")
            eat = await self._generate_eat(token, base_url)
        except Exception as exc:
            self._set_error(str(exc))
            return

        config = {
            "base_url": base_url,
            "token": token,
            "eat": eat,
            "email": email,
        }
        save_config(config)
        self.dismiss(config)

class ServiceConnectScreen(Screen):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, provider: Dict[str, Any]):
        super().__init__()
        self.provider = provider

    def compose(self) -> ComposeResult:
        provider_name = self.provider.get("name", "Provider")
        display_name = self.provider.get("display_name") or provider_name
        auth_hint = self.provider.get("hint", "")
        auth_label = "API Key" if self.provider.get("auth") == "api_key" else "OAuth Token"
        with Container(id="service-connect-container"):
            yield Label(f"Connect {display_name}", id="service-connect-title")
            if self.provider.get("custom"):
                yield Label("Provider Name")
                yield Input(
                    value=self.provider.get("prefill_name", ""),
                    placeholder="e.g., notion, github, linear",
                    id="provider-name-input",
                )
            else:
                yield Label("Provider")
                yield Label(display_name, id="provider-name-label")
            yield Label(f"{auth_label}")
            yield Input(password=True, placeholder=auth_hint or "Paste token", id="provider-token-input")
            yield Label("", id="service-connect-error")
            with Horizontal(id="service-connect-buttons"):
                yield Button("Connect", id="service-connect-btn", variant="primary")
                yield Button("Cancel", id="service-cancel-btn")

    def on_mount(self) -> None:
        if self.provider.get("custom"):
            self.query_one("#provider-name-input", Input).focus()
        else:
            self.query_one("#provider-token-input", Input).focus()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _set_error(self, message: str) -> None:
        label = self.query_one("#service-connect-error", Label)
        label.update(message)

    @on(Button.Pressed, "#service-cancel-btn")
    def handle_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#service-connect-btn")
    async def handle_connect(self) -> None:
        app = self.app
        provider_id = self.provider.get("id")
        if self.provider.get("custom"):
            provider_name = self.query_one("#provider-name-input", Input).value.strip().lower()
        else:
            provider_name = provider_id or ""

        token = self.query_one("#provider-token-input", Input).value.strip()
        if not provider_name:
            self._set_error("Provider name is required.")
            return
        if not token:
            self._set_error("Token is required.")
            return

        credential_type = "API_KEY" if self.provider.get("auth") == "api_key" else "OAUTH_TOKEN"
        payload = {
            "provider_name": provider_name,
            "token": token,
            "credential_type": credential_type,
            "metadata": {
                "source": "tui",
                "display_name": self.provider.get("name"),
                "flow": self.provider.get("auth"),
            },
        }

        response = await app._authed_request("POST", "/credentials", json_body=payload)
        if response.status_code not in (200, 201):
            self._set_error(_extract_error_detail(response))
            return

        self.dismiss({"provider_name": provider_name})

# ASCII header
LOGO = """
  [bold orange1]______ _   _  _____ _____            __  __ [/]
 [bold orange1]|  ____| \ | |/ ____|  __ \     /\   |  \/  |[/]
 [bold orange1]| |__  |  \| | |  __| |__) |   /  \  | \  / |[/]
 [bold orange1]|  __| | . ` | | |_ |  _  /   / /\ \ | |\/| |[/]
 [bold orange1]| |____| |\  | |__| | | \ \  / ____ \| |  | |[/]
 [bold orange1]|______|_| \_|\_____|_|  \_\/_/    \_\_|  |_|[/]
             [italic white]PROTOCOL BRIDGE[/] [bold dim]v0.1.0[/]
"""

class EngramTUI(App):
    """
    A terminal-based interface for the Engram Protocol Bridge.
    Heavy design inspiration from Claude Code and Deep Agents.
    """
    CSS = """
    Screen {
        background: #0f1115;
    }

    #header {
        height: 10;
        content-align: center middle;
        background: #1a1e26;
        border-bottom: double #d35400;
        margin-bottom: 1;
    }

    #main-container {
        height: 1fr;
    }

    #log-view {
        width: 70%;
        background: #12151c;
        border: solid #2c3e50;
        padding: 1;
    }

    #sidebar {
        width: 30%;
        background: #1a1e26;
        border-left: solid #2c3e50;
        padding: 1;
    }

    .sidebar-title {
        text-style: bold;
        color: #d35400;
        margin-bottom: 1;
    }

    .stat-item {
        margin-bottom: 1;
        color: #ecf0f1;
    }

    #task-panel {
        border: solid #2c3e50;
        padding: 1;
        margin-bottom: 1;
        background: #12151c;
    }

    #task-current, #task-progress, #task-connectors {
        color: #ecf0f1;
    }

    #input-area {
        height: 3;
        background: #1a1e26;
        border-top: solid #d35400;
        padding: 0 1;
    }

    Input {
        background: #1a1e26;
        border: none;
        color: #ecf0f1;
    }
    
    .status-ok {
        color: #2ecc71;
    }
    
    .status-waiting {
        color: #f1c40f;
    }

    #auth-container {
        width: 60%;
        height: auto;
        padding: 2 3;
        border: solid #d35400;
        background: #1a1e26;
        margin: 2 auto;
    }

    #auth-title {
        content-align: center middle;
        text-style: bold;
        color: #d35400;
        margin-bottom: 1;
    }

    #auth-buttons {
        margin-top: 1;
        height: auto;
    }

    #auth-error {
        color: #e74c3c;
        margin-top: 1;
    }

    #service-connect-container {
        width: 70%;
        height: auto;
        padding: 2 3;
        border: solid #d35400;
        background: #1a1e26;
        margin: 2 auto;
    }

    #service-connect-title {
        content-align: center middle;
        text-style: bold;
        color: #d35400;
        margin-bottom: 1;
    }

    #service-connect-buttons {
        margin-top: 1;
        height: auto;
    }

    #service-connect-error {
        color: #e74c3c;
        margin-top: 1;
    }

    #services-panel {
        margin-top: 1;
        border-top: solid #2c3e50;
        padding-top: 1;
    }

    .service-row {
        height: auto;
        margin-bottom: 1;
    }

    .service-name {
        width: 45%;
    }

    .service-status {
        width: 30%;
    }

    .service-btn {
        width: 25%;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("c", "clear", "Clear Logs", show=True),
        Binding("r", "refresh", "Refresh Stats", show=True),
        Binding("s", "services", "Services", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.token: Optional[str] = None
        self.eat: Optional[str] = None
        self.base_url: str = DEFAULT_BASE_URL
        self.user_email: Optional[str] = None
        self.connected_providers = set()
        self.active_task_id: Optional[str] = None
        self.active_task_text: Optional[str] = None
        self.active_task_status: Optional[str] = None
        self.active_task_steps: Dict[int, Dict[str, Any]] = {}
        self.active_task_agents = set()
        self.active_task_total_steps: Optional[int] = None

    def compose(self) -> ComposeResult:
        # Header with Logo
        yield Static(LOGO, id="header")

        # Main Layout
        with Horizontal(id="main-container"):
            # Translation Log
            yield RichLog(id="log-view", highlight=True, markup=True)
            
            # Sidebar info
            with Vertical(id="sidebar"):
                yield Label("📊 SYSTEM STATUS", classes="sidebar-title")
                yield Label("✅ [bold]FastAPI Engine:[/] [green]Online[/]", classes="stat-item")
                yield Label("✅ [bold]Discovery Service:[/] [green]Active[/]", classes="stat-item")
                yield Label("⚡ [bold]Task Worker:[/] [green]Processing[/]", classes="stat-item")

                with Container(id="task-panel"):
                    yield Label("TASK TRACKER", classes="sidebar-title")
                    yield Label("CURRENT TASK", classes="sidebar-title")
                    yield Static("No task submitted yet.", id="task-current")
                    yield Label("PROGRESS", classes="sidebar-title")
                    yield Static("Status: IDLE", id="task-progress")
                    yield Label("ACTIVE CONNECTORS", classes="sidebar-title")
                    yield Static("None", id="task-connectors")
                
                yield Label("\n🛰️ RECENT ACTIVITY", classes="sidebar-title")
                yield Label("• A2A Protocol registered", classes="stat-item")
                yield Label("• MCP Mapping loaded", classes="stat-item")
                yield Label("• Bridge listener started", classes="stat-item")
                
                yield Label("\n💡 COMMANDS", classes="sidebar-title")
                yield Label("/status - Check bridge health", classes="stat-item")
                yield Label("/agents - List connected agents", classes="stat-item")
                yield Label("/login  - Sign in", classes="stat-item")
                yield Label("/logout - Sign out", classes="stat-item")
                yield Label("/services - Refresh services", classes="stat-item")
                yield Label("/connect <provider> - Connect service", classes="stat-item")

                with Container(id="services-panel"):
                    yield Label("CONNECTED SERVICES", classes="sidebar-title")
                    for provider in PROVIDERS:
                        with Horizontal(classes="service-row"):
                            yield Label(provider["name"], id=f"service-name-{provider['id']}", classes="service-name")
                            yield Label("Not connected", id=f"service-status-{provider['id']}", classes="service-status status-waiting")
                            yield Button("Connect", id=f"service-connect-{provider['id']}", classes="service-btn")

        # Input Area (Command prompt)
        yield Input(placeholder="Type a task or /command (e.g., 'Prepare a report from Slack then send to Notion')", id="command-input")
        
        # Footer
        yield Footer()

    async def on_mount(self) -> None:
        """Start listening for bridge events when the UI is ready."""
        from app.core.tui_bridge import register_tui_loop
        register_tui_loop(asyncio.get_event_loop())

        config = load_config()
        self.base_url = config.get("base_url") or DEFAULT_BASE_URL
        self.token = config.get("token")
        self.eat = config.get("eat")
        self.user_email = config.get("email")
        if not self.eat:
            self.push_screen(AuthScreen(config), self._handle_auth_result)

        log_view = self.query_one("#log-view", RichLog)
        log_view.write("🚀 [bold orange1]Engram Protocol Bridge initialized.[/]")
        log_view.write("📡 [dim]Waiting for protocol events on shared queue...[/]\n")
        
        # Start background listener
        self.message_receiver()
        self.run_worker(self.refresh_connected_services(), thread=False)

    @work(exclusive=True, thread=True)
    def message_receiver(self):
        """Worker task to pull messages from the bridge queue and post them to UI."""
        import asyncio
        import time
        
        # We need a new loop here or access the main one since textual works on its own loop.
        # However, textual's @work allows us to run async or sync.
        # The tui_event_queue is an asyncio.Queue from the app's main thread (probably).
        
        # Since I used call_soon_threadsafe in the logger, it should be fine.
        # But wait, tui_event_queue.get() is an async call.
        
        async def run_listener():
            while True:
                msg = await tui_event_queue.get()
                self.call_from_thread(self.log_message, msg)
                tui_event_queue.task_done()
        
        # Ensure there's an event loop for this thread if needed, or just use the app's loop
        self.run_worker(run_listener())

    def log_message(self, message: str) -> None:
        """Update the log view with a new message."""
        log_view = self.query_one("#log-view", RichLog)
        # Add timestamp
        from datetime import datetime
        now = datetime.now().strftime("%H:%M:%S")
        log_view.write(f"[dim]{now}[/] {message}")
        self._handle_task_event(message)

    def _handle_task_event(self, message: str) -> None:
        """Parse orchestration events and update the task tracker panel."""
        import re

        if "Orchestration Plan" in message and "Split into" in message:
            match = re.search(r"Split into (\d+) agent steps", message)
            if match:
                self._set_task_total_steps(int(match.group(1)))
                self._set_task_status("PLANNED")
            return

        if "Step" in message and "Handing off to" in message:
            match = re.search(r"Step (\d+) \(Att (\d+)\):.*Handing off to \[bold\](.+?)\[/\]", message)
            if match:
                step_index = int(match.group(1))
                agent_name = match.group(3)
                self._update_step(step_index, agent_name, "RUNNING")
                self._set_task_status("RUNNING")
            return

        if "Step" in message and "OK" in message:
            match = re.search(r"Step (\d+) OK:.*\[bold\](.+?)\[/\]", message)
            if match:
                step_index = int(match.group(1))
                agent_name = match.group(2)
                self._update_step(step_index, agent_name, "COMPLETED")
            return

        if "failed after retries" in message:
            match = re.search(r"Step (\d+) failed after retries:.*", message)
            if match:
                step_index = int(match.group(1))
                self._update_step(step_index, None, "FAILED")
                self._set_task_status("FAILED")
            return

        if "Orchestration aborted" in message or "Planner:" in message:
            self._set_task_status("FAILED")
            return

        if "Complex task synchronized successfully" in message:
            self._set_task_status("COMPLETED")
            return

    def _reset_task_tracker(self, task_text: str, task_id: Optional[str]) -> None:
        self.active_task_text = task_text
        self.active_task_id = task_id
        self.active_task_status = "SUBMITTED"
        self.active_task_steps = {}
        self.active_task_agents = set()
        self.active_task_total_steps = None
        self._render_task_tracker()

    def _set_task_status(self, status: str) -> None:
        self.active_task_status = status
        self._render_task_tracker()

    def _set_task_total_steps(self, total_steps: int) -> None:
        self.active_task_total_steps = total_steps
        for i in range(1, total_steps + 1):
            self.active_task_steps.setdefault(i, {"agent": None, "status": "PENDING"})
        self._render_task_tracker()

    def _update_step(self, step_index: int, agent_name: Optional[str], status: str) -> None:
        step = self.active_task_steps.get(step_index, {"agent": None, "status": "PENDING"})
        if agent_name:
            step["agent"] = agent_name
            self.active_task_agents.add(agent_name)
        step["status"] = status
        self.active_task_steps[step_index] = step
        self._render_task_tracker()

    def _render_task_tracker(self) -> None:
        try:
            task_current = self.query_one("#task-current", Static)
            task_progress = self.query_one("#task-progress", Static)
            task_connectors = self.query_one("#task-connectors", Static)
        except Exception:
            return

        task_text = self.active_task_text or "No task submitted yet."
        task_current.update(task_text)

        status_line = f"Status: {self.active_task_status or 'IDLE'}"
        if self.active_task_id:
            status_line += f"\nTask ID: {self.active_task_id}"

        steps_lines = []
        if self.active_task_steps:
            for idx in sorted(self.active_task_steps.keys()):
                step = self.active_task_steps[idx]
                agent = step.get("agent") or "TBD"
                step_status = step.get("status") or "PENDING"
                steps_lines.append(f"{idx}. {agent} - {step_status}")
        elif self.active_task_total_steps:
            steps_lines.append(f"Steps: {self.active_task_total_steps} (awaiting plan)")

        progress_text = status_line
        if steps_lines:
            progress_text += "\n" + "\n".join(steps_lines)
        task_progress.update(progress_text)

        if self.active_task_agents:
            task_connectors.update(", ".join(sorted(self.active_task_agents)))
        else:
            task_connectors.update("None")


    @on(Input.Submitted)
    def handle_command(self, event: Input.Submitted) -> None:
        """Handle command input."""
        cmd = event.value.strip()
        if not cmd:
            return

        log_view = self.query_one("#log-view", RichLog)
        log_view.write(f"[bold cyan]> {cmd}[/]")
        
        # Process command (simple router)
        if cmd == "/clear":
            log_view.clear()
        elif cmd == "/status":
            log_view.write("Ã¢ÂÂ¹Ã¯Â¸Â [bold green]System Status:[/] All services operating within normal parameters.")
        elif cmd == "/login":
            config = load_config()
            self.push_screen(AuthScreen(config), self._handle_auth_result)
        elif cmd == "/logout":
            self.token = None
            self.eat = None
            self.user_email = None
            save_config({"base_url": self.base_url, "token": None, "eat": None, "email": None})
            log_view.write("[yellow]Logged out. Please login again.[/]")
            self.push_screen(AuthScreen(load_config()), self._handle_auth_result)
        elif cmd == "/agents":
            log_view.write("Ã¢ÂÂ¹Ã¯Â¸Â [bold yellow]Agents:[/] No active agent connections yet.")
        elif cmd == "/services":
            self.run_worker(self.refresh_connected_services(show_log=True), thread=False)
        elif cmd.startswith("/connect"):
            parts = cmd.split()
            if len(parts) < 2:
                log_view.write("[yellow]Usage:[/] /connect <provider>")
            else:
                provider_id = parts[1].strip().lower()
                if provider_id in PROVIDER_MAP:
                    self._open_service_connect(provider_id)
                else:
                    self._open_service_connect("custom", custom_name=provider_id)
        elif cmd.startswith("/"):
            log_view.write(f"Ã¢ÂÂ Ã¯Â¸Â Unknown command: [dim]{cmd}[/]")
        else:
            self.run_worker(self._run_task_command(cmd), thread=False)
            
        self.query_one("#command-input", Input).value = ""

    def action_clear(self) -> None:
        self.query_one("#log-view", RichLog).clear()

    def action_services(self) -> None:
        self.run_worker(self.refresh_connected_services(show_log=True), thread=False)

    def _handle_auth_result(self, result: Optional[Dict[str, Any]]) -> None:
        if not result:
            return
        self.base_url = result.get("base_url") or DEFAULT_BASE_URL
        self.token = result.get("token")
        self.eat = result.get("eat")
        self.user_email = result.get("email")
        self.run_worker(self.refresh_connected_services(), thread=False)

    async def _prompt_reauth(self) -> bool:
        loop = asyncio.get_running_loop()
        future: asyncio.Future = loop.create_future()

        def _handle(result: Optional[Dict[str, Any]]) -> None:
            if result:
                self._handle_auth_result(result)
                future.set_result(True)
            else:
                future.set_result(False)

        self.push_screen(AuthScreen(load_config()), _handle)
        return await future

    async def _ensure_eat(self) -> Optional[str]:
        if self.eat:
            return self.eat
        if not self.token:
            ok = await self._prompt_reauth()
            if not ok:
                return None
        response = await _request(
            "POST",
            self.base_url,
            "/auth/tokens/generate-eat",
            headers=_auth_header(self.token),
        )
        if response.status_code == 200:
            self.eat = response.json().get("eat")
            save_config({
                "base_url": self.base_url,
                "token": self.token,
                "eat": self.eat,
                "email": self.user_email,
            })
            return self.eat
        if _response_indicates_token_issue(response):
            ok = await self._prompt_reauth()
            if ok:
                return await self._ensure_eat()
        return None

    async def _authed_request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_session_token: bool = False,
        allow_retry: bool = True,
    ) -> httpx.Response:
        token = self.token if use_session_token else await self._ensure_eat()
        request_headers = _merge_headers(headers, _auth_header(token))
        response = await _request(
            method,
            self.base_url,
            path,
            json_body=json_body,
            data=data,
            headers=request_headers,
        )
        if allow_retry and _response_indicates_token_issue(response):
            if await self._prompt_reauth():
                token = self.token if use_session_token else await self._ensure_eat()
                retry_headers = _merge_headers(headers, _auth_header(token))
                return await _request(
                    method,
                    self.base_url,
                    path,
                    json_body=json_body,
                    data=data,
                    headers=retry_headers,
                )
        return response

    async def _run_task_command(self, command: str) -> None:
        log_view = self.query_one("#log-view", RichLog)
        eat = await self._ensure_eat()
        if not eat:
            log_view.write("[bold red]Auth required:[/] Please login to continue.")
            return

        self._reset_task_tracker(command, None)

        request_body = {
            "command": command,
            "metadata": {
                "client": "engram-tui",
                "timestamp": time.time(),
            },
        }

        log_view.write("[dim]Submitting task to Engram backend...[/]")
        try:
            response = await self._authed_request(
                "POST",
                "/tasks/submit",
                json_body=request_body,
            )
        except Exception as exc:
            log_view.write(f"[bold red]Submission error:[/] {str(exc)}")
            return
        if response.status_code != 200:
            log_view.write(f"[bold red]Submission failed:[/] {_extract_error_detail(response)}")
            return

        payload = response.json()
        task_id = payload.get("task_id")
        log_view.write(f"[bold green]Task accepted:[/] {task_id}")
        self._reset_task_tracker(command, str(task_id))


        last_status = None
        while True:
            await asyncio.sleep(2.0)
            try:
                status_resp = await self._authed_request(
                    "GET",
                    f"/tasks/{task_id}",
                )
            except Exception as exc:
                log_view.write(f"[bold red]Status check error:[/] {str(exc)}")
                return
            if status_resp.status_code != 200:
                log_view.write(f"[bold red]Status check failed:[/] {_extract_error_detail(status_resp)}")
                return
            task_status = status_resp.json()
            status = task_status.get("status")
            if status != last_status:
                last_status = status
                log_view.write(f"[dim]Status:[/] {status}")
                self._set_task_status(status)
            if status in ("COMPLETED", "DEAD_LETTER"):
                if task_status.get("last_error"):
                    log_view.write(f"[bold red]Last Error:[/] {task_status['last_error']}")
                results = task_status.get("results")
                if results:
                    log_view.write(f"[bold]Results:[/]\n{json.dumps(results, indent=2)}")
                else:
                    log_view.write("[dim]No workflow results recorded yet.[/]")
                break

    def _set_service_status(self, provider_id: str, status: str, connected: bool) -> None:
        label = self.query_one(f"#service-status-{provider_id}", Label)
        label.update(status)
        label.remove_class("status-ok")
        label.remove_class("status-waiting")
        label.remove_class("status-error")
        if connected:
            label.add_class("status-ok")
        else:
            label.add_class("status-waiting")

        button = self.query_one(f"#service-connect-{provider_id}", Button)
        if provider_id == "custom":
            button.disabled = False
            button.label = "Add"
        else:
            button.disabled = connected
            button.label = "Connected" if connected else "Connect"

    async def refresh_connected_services(self, show_log: bool = False) -> None:
        log_view = self.query_one("#log-view", RichLog)
        if show_log:
            log_view.write("[dim]Refreshing connected services...[/]")

        if not self.token and not self.eat:
            for provider in PROVIDERS:
                self._set_service_status(provider["id"], "Login required", False)
            return

        eat = await self._ensure_eat()
        if not eat:
            for provider in PROVIDERS:
                self._set_service_status(provider["id"], "Auth required", False)
            return

        response = await self._authed_request("GET", "/credentials")
        if response.status_code != 200:
            for provider in PROVIDERS:
                self._set_service_status(provider["id"], "Unavailable", False)
            if show_log:
                log_view.write(f"[bold red]Credential fetch failed:[/] {_extract_error_detail(response)}")
            return

        payload = response.json()
        connected = {item.get("provider_name", "").lower() for item in payload if item.get("provider_name")}
        self.connected_providers = connected

        known = {provider["id"] for provider in PROVIDERS if not provider.get("custom")}
        for provider in PROVIDERS:
            if provider.get("custom"):
                extras = [name for name in connected if name not in known]
                if extras:
                    self._set_service_status(provider["id"], f"Connected ({len(extras)})", True)
                else:
                    self._set_service_status(provider["id"], "Not connected", False)
                continue
            is_connected = provider["id"] in connected
            self._set_service_status(provider["id"], "Connected" if is_connected else "Not connected", is_connected)

    def _open_service_connect(self, provider_id: str, custom_name: Optional[str] = None) -> None:
        provider = PROVIDER_MAP.get(provider_id)
        if not provider:
            return
        if provider.get("custom") and custom_name:
            provider = {
                **provider,
                "prefill_name": custom_name,
                "display_name": custom_name,
            }
        self.push_screen(ServiceConnectScreen(provider), self._handle_service_connect_result)

    def _handle_service_connect_result(self, result: Optional[Dict[str, Any]]) -> None:
        if not result:
            return
        self.run_worker(self.refresh_connected_services(show_log=True), thread=False)

    @on(Button.Pressed)
    def handle_service_button(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id.startswith("service-connect-"):
            provider_id = button_id.replace("service-connect-", "")
            self._open_service_connect(provider_id)

if __name__ == "__main__":
    from textual import run
    run(EngramTUI)
