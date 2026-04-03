import os
import sys
import json
import yaml
import asyncio
import threading
import time
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List

import typer
import httpx
from pydantic import BaseModel, Field, HttpUrl
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn

# Constants
APP_NAME = "engram"
CONFIG_DIR = Path.home() / f".{APP_NAME}"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
DEFAULT_API_URL = "http://127.0.0.1:8000"

# Enums
class BackendPreference(str, Enum):
    MCP = "mcp"
    CLI = "cli"

# Models
class EngramConfig(BaseModel):
    api_url: str = Field(default=DEFAULT_API_URL, description="Base URL for the Engram API")
    eat_token: Optional[str] = Field(default=None, description="Engram Authorization Token (EAT)")
    backend_preference: BackendPreference = Field(default=BackendPreference.MCP, description="Default backend for tool execution")
    model_provider: str = Field(default="openai", description="Default AI model provider")
    verbose: bool = Field(default=False, description="Enable verbose logging")

class CLIContext:
    def __init__(self):
        self.config = EngramConfig()
        self.json_output = False
        self.console = Console()

    def load_config(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = yaml.safe_load(f)
                    if data:
                        self.config = EngramConfig(**data)
            except Exception as e:
                rprint(f"[bold red]Error loading config:[/] {e}")

    def save_config(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            # Use mode='json' to ensure Enums are serialized as strings
            yaml.dump(self.config.model_dump(mode='json'), f, default_flow_style=False)

    def output(self, data: Any, title: str = "Result"):
        if self.json_output:
            # Handle Pydantic models
            if isinstance(data, BaseModel):
                print(data.model_dump_json(indent=2))
            else:
                print(json.dumps(data, indent=2))
        else:
            if isinstance(data, str):
                rprint(Panel(data, title=f"[bold cyan]{title}[/]", border_style="cyan"))
            elif isinstance(data, dict):
                table = Table(title=title)
                table.add_column("Key", style="magenta")
                table.add_column("Value", style="green")
                for k, v in data.items():
                    table.add_row(str(k), str(v))
                self.console.print(table)
            elif isinstance(data, list):
                table = Table(title=title)
                if data and isinstance(data[0], dict):
                    keys = data[0].keys()
                    for key in keys:
                        table.add_column(key, style="cyan")
                    for item in data:
                        table.add_row(*(str(item.get(k, "")) for k in keys))
                else:
                    table.add_column("Item", style="cyan")
                    for item in data:
                        table.add_row(str(item))
                self.console.print(table)
            elif isinstance(data, BaseModel):
                self.output(data.model_dump(), title=title)

# Typer App
app = typer.Typer(
    name=APP_NAME,
    help="[bold green]Engram Protocol Bridge CLI[/] - Semantic Tool Orchestration",
    rich_markup_mode="rich",
    no_args_is_help=True
)

state = CLIContext()

@app.callback()
def main_callback(
    ctx: typer.Context,
    json: bool = typer.Option(False, "--json", help="Output in machine-readable JSON format"),
    config_path: Optional[Path] = typer.Option(None, "--config", help="Path to a custom config file"),
):
    """
    [bold]Engram CLI[/] - The universal translator for MCP tools and CLI agents.
    
    This CLI manages the foundational Phase 1 structure for tool discovery, 
    authentication, and multi-backend execution.
    """
    global CONFIG_FILE
    if config_path:
        CONFIG_FILE = config_path
    
    state.json_output = json
    state.load_config()
    ctx.obj = state

# --- Commands ---

@app.command()
def init():
    """
    Initialize the Engram configuration and directory structure.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Initializing config...", total=None)
        state.save_config()
        time.sleep(1)
        
    state.output(
        f"Initialized Engram directory at {CONFIG_DIR}\nConfig saved to {CONFIG_FILE}",
        title="Initialization Success"
    )

@app.command()
def info():
    """
    Display current CLI configuration and system status.
    """
    status = {
        "Config Path": str(CONFIG_FILE),
        "API URL": state.config.api_url,
        "Backend": state.config.backend_preference.value,
        "Auth Status": "Authenticated" if state.config.eat_token else "Anonymous",
        "EAT Token": "****" + state.config.eat_token[-4:] if state.config.eat_token else "None"
    }
    state.output(status, title="System Information")

# --- Auth Subgroup ---
auth_app = typer.Typer(help="Manage authentication and EAT (Engram Authorization Tokens)")
app.add_typer(auth_app, name="auth")

@auth_app.command("login")
def auth_login(email: str = typer.Option(..., prompt=True)):
    """
    Authenticate with the Engram backend to retrieve an EAT.
    """
    # This is a placeholder for the actual login logic
    rprint(f"[yellow]Initiating login flow for {email}...[/]")
    # In a real scenario, we'd call the /auth/login endpoint
    fake_token = "eat_live_9a2b3c4d5e6f7g8h9i0j"
    state.config.eat_token = fake_token
    state.save_config()
    state.output({"email": email, "eat": fake_token}, title="Login Successful")

@auth_app.command("token-set")
def auth_token_set(token: str):
    """
    Manually set the Engram Authorization Token (EAT).
    """
    state.config.eat_token = token
    state.save_config()
    rprint(f"✅ EAT token updated in {CONFIG_FILE}")

@auth_app.command("status")
def auth_status():
    """
    Check current authentication status.
    """
    if state.config.eat_token:
        state.output({"status": "authenticated", "token_preview": state.config.eat_token[:10] + "..."})
    else:
        state.output({"status": "unauthenticated"}, title="Authentication Status")

# --- Config Subgroup ---
config_app = typer.Typer(help="View and modify CLI configuration")
app.add_typer(config_app, name="config")

@config_app.command("show")
def config_show():
    """
    Display the current configuration.
    """
    state.output(state.config, title="Current Configuration")

@config_app.command("set")
def config_set(
    key: str, 
    value: str
):
    """
    Set a configuration value. (e.g., api_url, backend_preference)
    """
    if hasattr(state.config, key):
        # Basic type conversion
        current_val = getattr(state.config, key)
        if isinstance(current_val, bool):
            setattr(state.config, key, value.lower() == "true")
        elif isinstance(current_val, int):
            setattr(state.config, key, int(value))
        else:
            setattr(state.config, key, value)
        
        state.save_config()
        rprint(f"✅ Set [bold]{key}[/] to [bold]{value}[/]")
    else:
        rprint(f"[bold red]Error:[/] Unknown config key '{key}'")

# --- Tool Subgroup (Core Features) ---
tool_app = typer.Typer(help="Discover and manage tools (MCP & CLI)")
app.add_typer(tool_app, name="tools")

@tool_app.command("discover")
def tool_discover(query: Optional[str] = typer.Argument(None)):
    """
    Discover available tools across all connected protocols.
    """
    # Placeholder for tool discovery logic
    tools = [
        {"id": "slack.post_message", "type": "mcp", "description": "Post a message to Slack"},
        {"id": "github.create_issue", "type": "mcp", "description": "Create a new GitHub issue"},
        {"id": "local.list_files", "type": "cli", "description": "List files in directory"}
    ]
    if query:
        tools = [t for t in tools if query.lower() in t["id"].lower()]
    
    state.output(tools, title=f"Discovery Results: {query or 'All'}")

# --- Runtime Command (Existing functionality) ---

@app.command()
def run(
    host: str = typer.Option("127.0.0.1", help="Host to bind the backend"),
    port: int = typer.Option(8000, help="Port to run the backend"),
    debug: bool = typer.Option(False, "--debug", help="Start in debug mode")
):
    """
    Start the Engram Protocol Bridge backend and TUI dashboard.
    """
    from app.cli import start_runtime # We'll need to refactor this slightly or just import it
    # For now, we'll try to use the legacy start_runtime logic
    # but we need to avoid circular imports. 
    # Since we are overwriting app/cli.py, we should include the runtime logic here.
    
    _start_legacy_runtime(host, port, "debug" if debug else None)

def _start_legacy_runtime(host: str, port: int, initial_screen: Optional[str]):
    """Refactored version of the original start_runtime logic."""
    try:
        import uvicorn
        from app.main import app as fastapi_app
        from tui.app import EngramTUI
    except ImportError as e:
        rprint(f"❌ [bold red]Error:[/] Missing dependencies: {e}")
        return

    rprint(Panel.fit(
        "[bold orange1] ENGRAM PROTOCOL BRIDGE [/]\n[dim]Multi-Protocol Semantic Agent Translation[/]",
        subtitle=f"[bold]v0.1.0 | Gateway: {host}:{port}[/]",
        border_style="orange1"
    ))

    # Start API in background thread
    def run_api():
        try:
            uvicorn.run(fastapi_app, host=host, port=port, log_level="warning", access_log=False)
        except Exception as e:
            rprint(f"\n❌ [bold red]Backend Failed:[/] {e}")
            os._exit(1)
    
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    time.sleep(1.5)
    rprint(" ✅ [bold green]Backend Ready.[/]")
    
    # Start TUI
    try:
        tui = EngramTUI(base_url=f"http://{host}:{port}/api/v1")
        if initial_screen:
            tui.initial_screen = initial_screen
        tui.run()
    except Exception as e:
        rprint(f"❌ [bold red]TUI Error:[/] {e}")
        sys.exit(1)

if __name__ == "__main__":
    app()
