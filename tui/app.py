from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, RichLog, Input, Label
from textual.binding import Binding
from textual import on, work
import asyncio
from app.core.tui_bridge import tui_event_queue

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
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("c", "clear", "Clear Logs", show=True),
        Binding("r", "refresh", "Refresh Stats", show=True),
    ]

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
                yield Label("/help   - Get command list", classes="stat-item")

        # Input Area (Command prompt)
        yield Input(placeholder="Type a command or press Enter to continue...", id="command-input")
        
        # Footer
        yield Footer()

    async def on_mount(self) -> None:
        """Start listening for bridge events when the UI is ready."""
        from app.core.tui_bridge import register_tui_loop
        register_tui_loop(asyncio.get_event_loop())

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
            log_view.write("ℹ️ [bold green]System Status:[/] All services operating within normal parameters.")
        elif cmd == "/agents":
            log_view.write("ℹ️ [bold yellow]Agents:[/] No active agent connections yet.")
        else:
            log_view.write(f"⚠️ Unknown command: [dim]{cmd}[/]")
            
        self.query_one("#command-input", Input).value = ""

    def action_clear(self) -> None:
        self.query_one("#log-view", RichLog).clear()

if __name__ == "__main__":
    from textual import run
    run(EngramTUI)
