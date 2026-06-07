"""ClayForge CLI - Typer-based command line interface.

Commands:
- new: Scaffold a new project
- run: Run a ClayForge application (supports --app from source tree)
- showcase: Launch the official beautiful multi-section showcase (the living demo)
- deploy: Real production templates (Dockerfile, railway.toml, fly.toml, etc.) + guidance. Use --dir to write files.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..deploy import get_template_content, write_templates

__version__ = "0.2.0-alpha"

app = typer.Typer(
    name="clayforge",
    help="ClayForge — Beautiful, AI-native Python web apps with zero boilerplate.\n\n"
    "Key commands: new, run, showcase (the living demo), deploy.",
    add_completion=True,
    rich_markup_mode="rich",
)
console = Console()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show ClayForge version and exit.",
        is_eager=True,
    ),
) -> None:
    if version:
        import platform
        import sys

        console.print(
            f"[bold cyan]ClayForge[/bold cyan] v{__version__}\n"
            f"Python {sys.version.split()[0]} on {platform.system()} {platform.release()}"
        )
        raise typer.Exit()


@app.command()
def new(
    project_name: str = typer.Argument(..., help="Name of the new project directory"),
    template: str = typer.Option(
        "default",
        "--template",
        "-t",
        help="Project template (default | minimal | grok-heavy)",
    ),
) -> None:
    """Scaffold a new ClayForge project with beautiful defaults."""
    target = Path(project_name).resolve()

    if target.exists():
        console.print(f"[red]Error:[/red] Directory '{project_name}' already exists.")
        raise typer.Exit(1)

    target.mkdir(parents=True)

    # Minimal viable scaffold (will be greatly expanded in later phases)
    (target / "app.py").write_text(_get_default_app_template(), encoding="utf-8")
    (target / ".env.example").write_text(
        "# Copy this file to .env (or export the var) for real Grok streaming.\n"
        "# ClayForge works perfectly without any key (gorgeous simulation fallback).\n"
        "# Only set this if you want token-by-token from xAI in GrokChat / examples.\n"
        "XAI_API_KEY=your_xai_key_here\n",
        encoding="utf-8",
    )
    (target / "README.md").write_text(
        f"""# {project_name}

Built with ClayForge — beautiful, reactive Python web apps.

## Run it

    cd {project_name}
    clayforge run

## Protect a page with auth + query the DB

Add this (copy-paste friendly) to your `app.py`:

```python
from clayforge import Auth, Database
import clayforge as cf

auth = Auth()          # signed cookies, @require_login (one line)
db = Database()        # sqlite:///./clayforge.db — swap URL for Postgres

@app.page("/dashboard")
@auth.require_login
def dashboard(user=None):
    u = user or auth.get_current_user()
    # Simple protected query — data scoped to the logged-in user
    items = db.query(
        "SELECT id, title, done FROM todos WHERE user_id = ? ORDER BY id",
        (u["id"],) if u else (0,),
    )

    cf.ui.title(f"Hello {{u.get('name', 'there') if u else 'guest'}}")
    for it in items:
        cf.ui.text(f"• {{it['title']}}")
```

See complete patterns:
- `examples/auth_db_todo.py`
- `examples/internal_crm_with_auth.py`

(For production extras: `pip install "clayforge[auth,db]"`)

## Discover more instantly


- `clayforge showcase` — beautiful multi-section demo (dashboards, Grok, agents, forms…)
- Theming, custom components, and more in the docs

Edit `app.py`, save — UI updates live over WebSocket. Zero HTML/JS/CSS.
""",
        encoding="utf-8",
    )
    (target / "requirements.txt").write_text("clayforge\n", encoding="utf-8")

    # Create pages/ and components/ folders for good habits
    (target / "pages").mkdir()
    (target / "components").mkdir()
    (target / "pages" / "__init__.py").write_text("", encoding="utf-8")
    (target / "components" / "__init__.py").write_text("", encoding="utf-8")

    console.print(
        Panel(
            Text.from_markup(
                f"[bold green]+[/bold green] Created new ClayForge project at [bold]{project_name}[/bold]\n\n"
                "Next steps:\n"
                f"  [cyan]cd {project_name}[/cyan]\n"
                "  [cyan]clayforge run[/cyan]\n\n"
                "Edit [bold]app.py[/bold] and watch the magic happen."
            ),
            title="[bold cyan]ClayForge[/bold cyan]",
            border_style="cyan",
        )
    )


def _get_default_app_template() -> str:
    return '''"""
ClayForge Application — Beautiful, reactive, pure Python.

Run with:
    clayforge run

# =============================================================================
# NEW TO CLAYFORGE? START HERE:
# =============================================================================
#

#   The single best first command (the real hero demo):
#
#       clayforge showcase
#
#   Full polished multi-tab experience with dedicated GrokChat + real
#   AgentCanvas Research Swarm (Agent Vision tab), live dashboards, etc.
#   (The showcase *is* our showcase — no separate gallery.)
#
# Quick minimal starter: see examples/00_minimal.py
#
# Theming:
#       import clayforge as cf
#       cf.set_theme("dark")     # or "light", cf.Theme(...)
#
# Auth + DB one-liners:
#       from clayforge import auth, db
#
# Best patterns after the showcase:
#       examples/00_minimal.py
#       examples/03_grok_chat.py
#       examples/04_multi_agent_vision.py
#
# Pure Python + instant reactive WS updates.
# =============================================================================
"""

import clayforge as cf

app = cf.App(
    title="My ClayForge App",
    description="Built in minutes with the 2026 AI-native framework.",
)

@app.page("/")
def home():
    """Main page — written in pure Python with zero boilerplate."""

    cf.ui.title("Welcome to ClayForge")
    cf.ui.subtitle("Stunning UIs. Reactive WebSockets. First-class Grok.")

    with cf.ui.row(gap="6"):
        with cf.ui.card(title="Zero Boilerplate", subtitle="Just Python"):
            cf.ui.text("Edit this file, save, and the UI updates instantly via WebSocket.")
            cf.ui.text("No HTML. No CSS. No JavaScript. No full reruns.")

            # Real buttons with server roundtrips — click to see toast + console log
            def say_hello():
                print("[ClayForge] Hello button clicked on the server!")

            cf.ui.button("Say hello", variant="primary", classes="mt-4", on_click=say_hello)

            # New components added in this milestone
            cf.ui.divider(classes="my-3")
            cf.ui.badge("LIVE", variant="success")
            cf.ui.badge("Python", variant="info", classes="ml-2")

        with cf.ui.card(title="AI-Native", subtitle="Grok + Agents"):
            cf.ui.markdown("Drop in `GrokChat(...)` or `AgentCanvas(...)` and get production-grade streaming interfaces in one line.")
            cf.ui.text_input(placeholder="Ask Grok anything...", classes="mt-4")

    cf.ui.footer("Made with ClayForge • MIT License • Pure Python • 2026")

    # ------------------------------------------------------------------
    # Auth + Database — first-class, zero boilerplate (copy-paste example)
    # ------------------------------------------------------------------
    # from clayforge import Auth, Database
    # auth = Auth()                 # signed cookie sessions (one-line protection)
    # db = Database()               # sqlite by default — trivial Postgres upgrade
    #
    # @app.page("/dashboard")
    # @auth.require_login
    # def dashboard(user=None):
    #     """Protected page + simple DB query (scoped to the logged-in user)."""
    #     u = user or auth.get_current_user()
    #     # Real query — lives in your SQLite (or Postgres). Re-renders instantly.
    #     items = db.query(
    #         "SELECT id, title, done FROM todos WHERE user_id = ? ORDER BY id",
    #         (u["id"],) if u else (0,),
    #     )
    #     cf.ui.title(f"Hello {u.get('name', 'there') if u else 'guest'}")
    #     for it in items:
    #         cf.ui.text(f"• {it['title']}")
    #
    # Full demos: examples/auth_db_todo.py  •  examples/internal_crm_with_auth.py
    # (pip install "clayforge[auth,db]" unlocks production password hashing + async)
'''


@app.command()
def run(
    app_path: str = typer.Option(
        "app:app",
        "--app",
        "-a",
        help="Import path to ClayForge app (module:instance)",
    ),
    host: str = typer.Option("127.0.0.1", "--host", help="Bind host"),
    port: int = typer.Option(8000, "--port", "-p", help="Bind port"),
    reload: bool = typer.Option(True, "--reload/--no-reload", help="Enable auto-reload (dev)"),
) -> None:
    """Run a ClayForge application with Uvicorn."""
    import os

    import uvicorn

    console.print(
        Panel(
            f"🚀 Starting [bold cyan]ClayForge[/bold cyan] at [bold]http://{host}:{port}[/bold]\n"
            "(Use --port 8001 if 8000 is busy. On Windows, kill previous python processes if you see bind errors.)",
            border_style="cyan",
        )
    )

    # Dynamically import the user's App (supports "app:app", "examples.foo:bar", etc.)
    # and wire it into the server BEFORE uvicorn imports the ASGI app.
    # This makes `clayforge new testapp && python -m clayforge run` (even without cd) work.
    try:
        if ":" in app_path:
            mod_name, attr = app_path.split(":", 1)
        else:
            mod_name, attr = app_path, "app"
        import importlib

        # Make cwd importable so "app" (from app.py created by `clayforge new`) resolves reliably
        import sys
        if str(Path.cwd()) not in sys.path:
            sys.path.insert(0, str(Path.cwd()))

        mod = importlib.import_module(mod_name)
        user_app = getattr(mod, attr, None)
        if user_app is not None:
            from clayforge.core.app import App
            from clayforge.core.server import set_current_app

            if isinstance(user_app, App):
                set_current_app(user_app)
            os.environ["CLAYFORGE_APP"] = app_path
    except Exception as exc:  # noqa: BLE001
        console.print(
            f"[yellow]Warning:[/yellow] Could not pre-mount {app_path}: {exc}\n"
            "Tip: cd into your project directory (the one containing app.py), or use --app path/to/yourapp:app\n"
            "If you see port errors later, another server may be running — kill it or use --port 8001"
        )

    # The real server lives in core.server — we will import the mounted app there
    try:
        uvicorn.run(
            "clayforge.core.server:app",
            host=host,
            port=port,
            reload=reload,
            reload_dirs=["."] if reload else None,
            log_level="info",
        )
    except OSError as e:
        if "10048" in str(e) or "address already in use" in str(e).lower():
            console.print(f"[red]Port {port} is already in use.[/red] Kill the other process or use --port 8001.")
        elif "10013" in str(e) or "access" in str(e).lower():
            console.print("[red]Access denied binding the port.[/red] Try a different --port or check antivirus/firewall.")
        else:
            raise
        raise typer.Exit(1) from e


@app.command()
def showcase() -> None:
    """Launch the official ClayForge Showcase — the beautiful multi-section living demo (dedicated GrokChat tab, framework-native Research Swarm / real AgentCanvas in Agent Vision tab, dashboards, forms, theming, and more).

    After a plain `pip install clayforge`, this command creates (or refreshes) a local
    `showcase_demo.py` file in your current directory. That file + the server give you
    the exact full rich experience you see when cloning the repo and running
    `python -m clayforge showcase`.
    """
    import os
    from datetime import datetime
    from pathlib import Path

    import uvicorn

    cwd = Path.cwd()
    demo_file = cwd / "showcase_demo.py"

    console.print(
        Panel(
            "Launching the ClayForge Showcase — our hero demo.\n\n"
            "Dedicated tabs: GrokChat + framework-native Agent Vision (real AgentCanvas + public API, bubble polish).\n"
            "Dashboards with live mutations, forms, theming, and more. Pure Python. Zero boilerplate.\n\n"
            f"A local `showcase_demo.py` (the full version) will be written to: {demo_file}",
            title="[bold cyan]ClayForge Showcase[/bold cyan]",
            border_style="cyan",
        )
    )

    # Write/refresh the local showcase_demo.py so users have the "full version" as
    # an inspectable file in their project (per the design discussed).
    # The actual rich behavior comes from the packaged clayforge.showcase.
    try:
        template = None
        try:
            # Preferred: read from the installed package (works after plain pip install)
            import importlib.resources as pkg_resources
            template = (pkg_resources.files("clayforge") / "showcase_demo.py").read_text(encoding="utf-8")
        except Exception:
            # Dev fallback: read the one at the repo root when running from source
            # (e.g. PYTHONPATH=src python -m clayforge showcase)
            root_demo = Path(__file__).parent.parent.parent.parent / "showcase_demo.py"
            if root_demo.exists():
                template = root_demo.read_text(encoding="utf-8")

        if template:
            header = (
                f"# This file was (re)generated by `clayforge showcase` on {datetime.now().isoformat()}\n"
                "# It launches the full official ClayForge Showcase (the exact rich experience\n"
                "# the team sees from a git clone).\n"
                "# Feel free to edit, version-control, or lift patterns from it.\n\n"
            )
            demo_file.write_text(header + template, encoding="utf-8")
            console.print(f"[green]Wrote/updated[/green] {demo_file}")
        else:
            raise RuntimeError("Could not locate showcase_demo.py template")
    except Exception as exc:  # noqa: BLE001
        console.print(f"[yellow]Note:[/yellow] Could not write local showcase_demo.py ({exc}). "
                      "The server will still run the full rich demo from the package.")

    # Mount and run the real packaged rich showcase (this is what matches the
    # full experience from `python -m clayforge showcase` in the source tree).
    loaded = False
    try:
        from clayforge.core.app import App as ClayForgeApp
        from clayforge.core.server import set_current_app
        from clayforge.showcase import app as showcase_cf_app

        if isinstance(showcase_cf_app, ClayForgeApp):
            set_current_app(showcase_cf_app)
            os.environ["CLAYFORGE_APP"] = "clayforge.showcase:app"
            loaded = True
    except Exception as exc:  # noqa: BLE001
        console.print(
            Panel(
                f"[yellow]Could not load the full packaged showcase.[/yellow]\n\n{exc}\n\n"
                "Quick alternatives:\n"
                "  clayforge new myapp && cd myapp && clayforge run\n"
                "  python -m clayforge run --app examples.03_grok_chat:app\n\n"
                "For the absolute latest developer version from source:\n"
                "  git clone https://github.com/JohnDClay/clayforge\n"
                "  cd clayforge\n"
                '  pip install -e ".[viz,grok]"\n'
                "  python -m clayforge showcase",
                title="[bold cyan]ClayForge Showcase[/bold cyan]",
                border_style="cyan",
            )
        )
        raise typer.Exit(1) from None

    if loaded:
        try:
            uvicorn.run(
                "clayforge.core.server:app",
                host="127.0.0.1",
                port=8000,
                log_level="info",
            )
        except OSError as e:
            if "10048" in str(e) or "address already in use" in str(e).lower():
                console.print("[red]Port 8000 is already in use.[/red] Kill the previous server or run with a different port.")
            elif "10013" in str(e) or "access" in str(e).lower():
                console.print("[red]Access denied binding port 8000.[/red] Try killing other python processes or use a different port.")
            else:
                raise
            raise typer.Exit(1) from e


@app.command()
def deploy(
    platform: str | None = typer.Option(
        None,
        "--platform",
        "-p",
        help="Target platform (docker, railway, fly, vercel, hf). Omit for overview.",
    ),
    project_dir: Path | None = typer.Option(  # noqa: B008
        None,
        "--dir",
        "-d",
        help="Write ready-to-use template files into this directory (e.g. your project root).",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing template files when using --dir.",
    ),
) -> None:
    """Production deployment helper with real copy-paste templates.

    ClayForge apps are standard ASGI/FastAPI apps. Deploy anywhere.
    Always use the correct extras for production:
        pip install clayforge
    """
    platform_map = {
        "docker": ["Dockerfile", ".dockerignore", "docker-compose.yml"],
        "railway": ["railway.toml", "Dockerfile", ".dockerignore"],
        "fly": ["fly.toml", "Dockerfile", ".dockerignore"],
        "vercel": ["vercel.json"],
        "hf": ["Dockerfile", ".dockerignore"],  # HF Spaces Docker path recommended
    }

    all_platforms = list(platform_map.keys())

    if platform is None or platform.lower() not in all_platforms:
        # Overview
        console.print(
            Panel(
                "[bold cyan]ClayForge Deploy[/bold cyan]\n\n"
                "ClayForge apps are plain FastAPI/ASGI — deploy to any Python host.\n\n"
                "[bold]Production extras (highly recommended):[/bold]\n"
                '  pip install clayforge\n\n'
                "[bold]Write real templates into your project:[/bold]\n"
                "  clayforge deploy --platform docker --dir .\n"
                "  clayforge deploy -p railway -d myapp\n\n"
                "[bold]Available platforms:[/bold] " + ", ".join(all_platforms) + "\n\n"
                "Templates are real files shipped with the package (inspect in site-packages or on GitHub).",
                title="Deployment Guidance",
                border_style="cyan",
            )
        )
        for key in all_platforms:
            files = ", ".join(platform_map[key])
            console.print(f"  [bold]{key}[/bold] -> {files}")
        console.print("\n[dim]Run with --platform + --dir to write files now.[/dim]")
        return

    key = platform.lower()
    template_files = platform_map[key]

    # Always show nice guidance + the actual file contents for easy copy
    console.print(
        Panel(
            f"[bold]{key.upper()}[/bold]\n\n"
            f"Best templates for this platform: [cyan]{', '.join(template_files)}[/cyan]\n\n"
            "Install production extras:\n"
            '  pip install clayforge\n\n'
            "Then use --dir to write the files into your project root.",
            title=f"[cyan]ClayForge Deploy — {key}[/cyan]",
            border_style="cyan",
        )
    )

    # Show contents of primary template(s) for immediate copy-paste
    for fname in template_files[:2]:  # keep output short & high signal
        try:
            content = get_template_content(fname)
            console.print(f"\n[bold yellow]{fname}[/bold yellow]")
            console.print(f"[dim]{'-' * 40}[/dim]")
            console.print(content)
            console.print(f"[dim]{'-' * 40}[/dim]")
        except Exception:
            pass

    # Write files if requested
    if project_dir is not None:
        try:
            written = write_templates(
                project_dir,
                filenames=template_files,
                overwrite=overwrite,
            )
            if written:
                console.print(
                    Panel(
                        "Wrote production deployment templates:\n\n"
                        + "\n".join(f"  • {p.name} -> {p}" for p in written)
                        + "\n\nNext: review, commit, and deploy.",
                        title="[green]Templates Written[/green]",
                        border_style="green",
                    )
                )
            else:
                console.print(
                    "[yellow]No new files written[/yellow] (already existed; use --overwrite to replace)."
                )
        except Exception as exc:
            console.print(f"[red]Error writing templates:[/red] {exc}")
            raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
