"""
Agent Translator Middleware Daemon
Unifies the FastAPI semantic bridge endpoints and the Textual TUI dashboard.
"""
import sys
import os
import threading
import uvicorn
import asyncio
from typing import Any

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Label, DataTable
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding
from app.main import app as fastapi_app
from app.core.config import settings
from dotenv import load_dotenv

load_dotenv()

class DashboardApp(App):
    """
    A high-end Textual TUI for the Agent Translator Middleware.
    Provides real-time visibility into the universal bridge operations.
    """
    
    TITLE = "AGENT TRANSLATOR DAEMON"
    SUB_TITLE = "Multi-Protocol Semantic Bridge (A2A ⇌ MCP ⇌ ACP)"
    
    CSS = """
    Screen {
        background: #0f172a;
        color: #e2e8f0;
    }
    
    Header {
        background: #1e293b;
        color: #38bdf8;
        border-bottom: double #38bdf8;
        text-style: bold;
    }
    
    Footer {
        background: #1e293b;
        color: #94a3b8;
    }
    
    #main-container {
        padding: 1 4;
    }
    
    .status-card {
        border: heavy #38bdf8;
        background: #1e293b;
        padding: 1 2;
        margin-top: 1;
        height: auto;
    }
    
    .section-title {
        color: #7dd3fc;
        text-style: bold underline;
        margin-bottom: 1;
    }
    
    .info-line {
        margin-bottom: 0;
    }
    
    .highlight {
        color: #fbbf24;
        text-style: bold;
    }
    
    .success {
        color: #22c55e;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit Daemon"),
        Binding("d", "toggle_dark", "Toggle Appearance"),
        Binding("r", "refresh", "Refresh View"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main-container"):
            with Vertical():
                yield Static("[bold #38bdf8]CORE CLUSTER STATUS[/]", classes="section-title")
                with Container(classes="status-card"):
                    yield Static(f"• Semantic Bridge URL: [link=http://localhost:8000]http://localhost:8000[/]")
                    yield Static(f"• API Gateway: [/api/v1/]")
                    yield Static(f"• Monitoring: [/metrics]")
                    yield Static(f"• Environment: [#fbbf24]{os.getenv('ENVIRONMENT', 'DEVELOPMENT')}[/]")
                
                yield Static("")
                yield Static("[bold #38bdf8]ACTIVE MODULES[/]", classes="section-title")
                with Horizontal():
                    yield Static(" [success]✔[/] Core Engine\n [success]✔[/] Memory Silo\n [success]✔[/] Semantic Mapper\n [success]✔[/] Discovery Svc", classes="status-card")
                    yield Static(" [success]✔[/] Task Worker\n [success]✔[/] Protocol Graph\n [success]✔[/] Redis Cache\n [#fbbf24]⚠[/] ML Fallback", classes="status-card")
                
        yield Footer()

    def action_refresh(self) -> None:
        """Manually refresh the dashboard content."""
        self.notify("Refreshing system metrics...", title="Update", severity="information")

def run_uvicorn():
    """Starts the FastAPI application via Uvicorn in a dedicated thread."""
    # Run uvicorn without the reload feature when running inside another app
    uvicorn.run(
        fastapi_app, 
        host="0.0.0.0", 
        port=8000, 
        log_level="warning", # Reduce log noise in TUI
        access_log=False
    )

if __name__ == "__main__":
    # 1. Initialize API Gateway in Background
    api_thread = threading.Thread(target=run_uvicorn, daemon=True)
    api_thread.start()

    # 2. Launch TUI Dashboard in Foreground
    tui_app = DashboardApp()
    tui_app.run()
