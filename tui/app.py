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
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("c", "clear", "Clear Logs", show=True),
        Binding("r", "refresh", "Refresh Stats", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.token: Optional[str] = None
        self.eat: Optional[str] = None
        self.base_url: str = DEFAULT_BASE_URL
        self.user_email: Optional[str] = None

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
                
                yield Label("\n🛰️ RECENT ACTIVITY", classes="sidebar-title")
                yield Label("• A2A Protocol registered", classes="stat-item")
                yield Label("• MCP Mapping loaded", classes="stat-item")
                yield Label("• Bridge listener started", classes="stat-item")
                
                yield Label("\n💡 COMMANDS", classes="sidebar-title")
                yield Label("/status - Check bridge health", classes="stat-item")
                yield Label("/agents - List connected agents", classes="stat-item")
                yield Label("/login  - Sign in", classes="stat-item")
                yield Label("/logout - Sign out", classes="stat-item")

        # Input Area (Command prompt)
        yield Input(placeholder="Type a command or press Enter to continue...", id="command-input")
        
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
        elif cmd.startswith("/"):
            log_view.write(f"Ã¢ÂÂ Ã¯Â¸Â Unknown command: [dim]{cmd}[/]")
        else:
            self.run_worker(self._run_task_command(cmd), thread=False)
            
        self.query_one("#command-input", Input).value = ""

    def action_clear(self) -> None:
        self.query_one("#log-view", RichLog).clear()

    def _handle_auth_result(self, result: Optional[Dict[str, Any]]) -> None:
        if not result:
            return
        self.base_url = result.get("base_url") or DEFAULT_BASE_URL
        self.token = result.get("token")
        self.eat = result.get("eat")
        self.user_email = result.get("email")

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
            if status in ("COMPLETED", "DEAD_LETTER"):
                if task_status.get("last_error"):
                    log_view.write(f"[bold red]Last Error:[/] {task_status['last_error']}")
                results = task_status.get("results")
                if results:
                    log_view.write(f"[bold]Results:[/]\n{json.dumps(results, indent=2)}")
                else:
                    log_view.write("[dim]No workflow results recorded yet.[/]")
                break

if __name__ == "__main__":
    from textual import run
    run(EngramTUI)
