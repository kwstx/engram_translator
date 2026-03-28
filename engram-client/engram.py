import os
import json
import click
import httpx
import asyncio
import time
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

console = Console()

CONFIG_DIR = os.path.expanduser("~/.engram")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
DEFAULT_BASE_URL = "http://localhost:8000/api/v1"

def load_config() -> Dict[str, Any]:
    if not os.path.exists(CONFIG_FILE):
        return {"base_url": DEFAULT_BASE_URL, "token": None, "eat": None}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config: Dict[str, Any]):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

async def check_health(base_url: str) -> bool:
    root_url = base_url.replace("/api/v1", "")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(root_url)
            return response.status_code == 200
    except Exception:
        return False

def _auth_header(token: Optional[str]) -> Dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}

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

def _render_task_results(results: Optional[Dict[str, Any]]) -> None:
    if not results:
        console.print("[dim]No workflow results recorded yet.[/]")
        return
    console.print("\n[bold]Workflow Results:[/]")
    for agent_id, output in results.items():
        console.print(f"  [bold cyan]{agent_id}[/]")
        syntax = Syntax(json.dumps(output, indent=2), "json", theme="monokai", line_numbers=False)
        console.print(syntax)

@click.group()
def cli():
    """Engram Client (thin API client)."""
    pass

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
    base_url = config["base_url"]

    async def do_login():
        try:
            response = await _request(
                "POST",
                base_url,
                "/auth/login",
                data={"username": email, "password": password},
            )
            if response.status_code == 200:
                data = response.json()
                config["token"] = data["access_token"]
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
            else:
                console.print(f"[red]ERROR[/] Login failed: {response.text}")
        except Exception as e:
            console.print(f"[red]ERROR[/] Connection error: {str(e)}")

    asyncio.run(do_login())

@cli.command()
def status():
    """Check the status of the connection and the backend."""
    config = load_config()
    base_url = config["base_url"]

    table = Table(title="Engram Status", show_header=False, box=None)
    table.add_row("Base URL", base_url)

    async def get_status():
        is_up = await check_health(base_url)
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
        console.print("[red]ERROR[/] Missing session token. Please login first.")
        return

    async def do_generate():
        try:
            response = await _request(
                "POST",
                base_url,
                "/auth/tokens/generate-eat",
                headers=_auth_header(token),
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
        eat = await _ensure_eat(config)
        if not eat:
            console.print("[red]ERROR[/] Missing Engram Access Token (EAT). Please login first.")
            return

        request_body = {
            "command": task,
            "metadata": {
                "client": "engram-cli",
                "timestamp": time.time(),
            },
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task_description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Submitting task to Engram backend...", total=None)
            try:
                response = await _request(
                    "POST",
                    base_url,
                    "/tasks/submit",
                    json_body=request_body,
                    headers=_auth_header(eat),
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

        token = config.get("token") or eat
        last_status = None
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task_description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Waiting for workflow execution...", total=None)
            while True:
                await asyncio.sleep(poll_seconds)
                status_resp = await _request(
                    "GET",
                    base_url,
                    f"/tasks/{task_id}",
                    headers=_auth_header(token),
                )
                if status_resp.status_code != 200:
                    console.print(f"[red]ERROR[/] Status check failed: {status_resp.text}")
                    return
                task_status = status_resp.json()
                status = task_status.get("status")
                if status != last_status:
                    last_status = status
                    console.print(f"[dim]Status[/]: {status}")
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
            response = await _request(
                "POST",
                base_url,
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
    token = config.get("token") or config.get("eat")
    if not token:
        console.print("[red]ERROR[/] Missing token. Please login first.")
        return

    async def do_list():
        response = await _request(
            "GET",
            base_url,
            "/tasks",
            headers=_auth_header(token),
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

if __name__ == "__main__":
    cli()
