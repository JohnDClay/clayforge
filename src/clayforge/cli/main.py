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
# NEW TO CLAYFORGE? DISCOVER THE FULL POWER IMMEDIATELY:
# =============================================================================
#

#         Browse every UI primitive, try them live, copy ready-to-paste code.
#
#   clayforge showcase
#       → The beautiful multi-section experience (GrokChat, dashboards,
#         agent vision, forms, theming explorer, and more — all in one app).
#
# Theming (instant, powerful):
#       import clayforge as cf
#       cf.set_theme(cf.Theme.DARK)   # LIGHT, SYSTEM, or full cf.Theme(...)
#       # Build and register your own custom components:
#       cf.register_component(...)
#
# Auth + Database (production-grade, zero ceremony):
#       from clayforge import Auth, Database
#       auth = Auth()   # @auth.require_login on any @app.page or route
#       db = Database() # .query() / .execute() — sqlite by default (Postgres ready)
#       # Concrete protected page + simple query example is shown further down in this header.
#
# Clean, real-world examples (the best learning path):
#       examples/auth_db_todo.py
#       examples/internal_crm_with_auth.py
#       (See the full examples/ folder for patterns you can lift directly.)
#
# Everything else stays pure Python with instant reactive updates.
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
            f"🚀 Starting [bold cyan]ClayForge[/bold cyan] at [bold]http://{host}:{port}[/bold]",
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

        mod = importlib.import_module(mod_name)
        user_app = getattr(mod, attr, None)
        if user_app is not None:
            from clayforge.core.app import App
            from clayforge.core.server import set_current_app

            if isinstance(user_app, App):
                set_current_app(user_app)
            # Also set env for uvicorn reloader child processes
            os.environ["CLAYFORGE_APP"] = app_path
    except Exception as exc:  # noqa: BLE001
        console.print(f"[yellow]Warning:[/yellow] Could not pre-mount {app_path}: {exc}")

    # The real server lives in core.server — we will import the mounted app there
    uvicorn.run(
        "clayforge.core.server:app",
        host=host,
        port=port,
        reload=reload,
        reload_dirs=["."] if reload else None,
        log_level="info",
    )


@app.command()
def showcase() -> None:
    """Launch the official ClayForge Showcase — a beautiful multi-section experience with dedicated GrokChat tab (visual), Research Swarm/Agent Vision tab (Start runs multi-agent demo), dashboards, forms, theming, and more."""
    import os

    import uvicorn

    console.print(
        Panel(
            "Launching the ClayForge Showcase...\n\n"
            "Beautiful multi-section demo with dedicated tabs: GrokChat (visual-only with canned responses) and Agent Vision (static Research Swarm viz). Other sections cover theming, forms, live dashboard, etc. Use sidebar to switch.",
            title="[bold cyan]ClayForge Showcase[/bold cyan]",
            border_style="cyan",
        )
    )

    # We must always run through clayforge.core.server (the real ASGI app),
    # and mount the showcase ClayForgeApp into it. Directly passing
    # "showcase.app:app" to uvicorn fails because ClayForgeApp is not ASGI.
    try:
        from clayforge.core.app import App as ClayForgeApp
        from clayforge.core.server import set_current_app
        from showcase.app import app as showcase_cf_app

        if isinstance(showcase_cf_app, ClayForgeApp):
            set_current_app(showcase_cf_app)
            os.environ["CLAYFORGE_APP"] = "showcase.app:app"
    except Exception:  # noqa: BLE001
        console.print(
            Panel(
                "[yellow]Showcase demo modules not importable from current PYTHONPATH.[/yellow]\n\n"
                "The full `clayforge showcase` experience is the rich, self-hosted "
                "living demos that live in the ClayForge source repository.\n\n"
                "[bold]Recommended for full exploration:[/bold]\n"
                "  git clone https://github.com/JohnDClay/clayforge\n"
                "  cd clayforge\n"
                '  pip install -e ".[viz,grok,db,auth]"\n'
                "  python -m clayforge showcase\n\n"
                "After a plain `pip install clayforge`, use:\n"
                "  clayforge new myapp && cd myapp && clayforge run\n"
                "  clayforge deploy --help\n\n"
                "(Advanced: PYTHONPATH=/path/to/clayforge-repo still works.)",
                title="[bold cyan]ClayForge Showcase[/bold cyan]",
                border_style="cyan",
            )
        )

    uvicorn.run(
        "clayforge.core.server:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )


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
        pip install "clayforge[viz,grok]"
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
                '  pip install "clayforge[viz,grok]"\n\n'
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
            '  pip install "clayforge[viz,grok]"\n\n'
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
