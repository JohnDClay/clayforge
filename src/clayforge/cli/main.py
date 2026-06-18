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

    # Choose template (now implemented; default gives a nice interactive starter,
    # minimal is the absolute smallest runnable app.py).
    if template == "minimal":
        app_content = _get_minimal_app_template()
    else:
        # default (and future grok-heavy etc fall back to a clean but featureful default)
        app_content = _get_default_app_template()
    (target / "app.py").write_text(app_content, encoding="utf-8")
    (target / ".env.example").write_text(
        "# Copy this file to .env (or export the var) for real Grok streaming.\n"
        "# ClayForge works perfectly without any key (gorgeous simulation fallback).\n"
        "# Only set this if you want token-by-token from xAI in GrokChat / examples.\n"
        "XAI_API_KEY=your_xai_key_here\n",
        encoding="utf-8",
    )
    (target / "README.md").write_text(
        f"""# {project_name}

Built with **ClayForge** — beautiful reactive UIs in pure Python. Zero boilerplate.

## Run

    clayforge run

(From the project directory, or from the parent dir — auto-discovers unambiguous `app.py` projects.)

## Edit & iterate

Edit `app.py`, save — the UI updates live over WebSocket.

No HTML, CSS, or JS required.

## Add power (optional)

```bash
pip install "clayforge[grok,db,auth,viz]"
```

- Real Grok streaming & AgentCanvas: set `XAI_API_KEY` (see `.env.example`)
- Auth + DB: `from clayforge import auth, db`
- Viz: PlotlyChart, DataTable

See full patterns: `clayforge showcase`

## Multi-page apps
Use `@app.page("/dashboard")` (or bare `from clayforge import page`).

`pages/` dir + `import pages.xxx` (created on `clayforge new`) keeps things organized.
Navigation is just real paths.

## Production

    clayforge deploy --platform docker -d .
    # or railway, fly, etc. (real templates)
""",
        encoding="utf-8",
    )
    (target / "requirements.txt").write_text("clayforge\n", encoding="utf-8")

    # Standard .gitignore so new projects start clean (core + packaging hygiene)
    (target / ".gitignore").write_text(
        "__pycache__/\n"
        "*.py[cod]\n"
        "*$py.class\n"
        ".env\n"
        ".venv/\n"
        "venv/\n"
        "*.db\n"
        "clayforge.db\n"
        ".clayforge*\n"
        "dist/\n"
        "build/\n"
        "*.egg-info/\n",
        encoding="utf-8",
    )

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
                f"  [cyan]cd {project_name}[/cyan]  (recommended)\n"
                "  [cyan]clayforge run[/cyan]\n\n"
                "Edit [bold]app.py[/bold] and watch live updates. `clayforge run` works from parent dir too."
            ),
            title="[bold cyan]ClayForge[/bold cyan]",
            border_style="cyan",
        )
    )


def _get_default_app_template() -> str:
    """Clean, excellent, bloat-free default starter demonstrating recommended core patterns."""
    return '''"""
ClayForge app (via `clayforge new`).

Zero boilerplate starter. Edit and save for instant live UI.

Run:
    clayforge run
    # or: python app.py
"""

import clayforge as cf

app = cf.App(
    title="My ClayForge App",
    description="Built in minutes with the AI-native Python web framework.",
)


@app.page("/")
def home():
    """Recommended core pattern: App + @page + cf.ui.* + context managers + on_click handlers."""

    cf.ui.title("Welcome to ClayForge")
    cf.ui.subtitle("Stunning UIs • Pure Python • Live WebSocket reactivity")

    # Live state via closure list (battle-tested zero-boilerplate pattern)
    count = [0]

    def increment():
        count[0] += 1
        cf.ui.success(f"Clicked {count[0]}x - server roundtrip + WS update")

    # Demo first-class form + state (get_session_state + on_change)
    def on_prio(v):
        st = cf.get_session_state()
        st["prio"] = v
        cf.ui.success("Priority: " + str(v))

    with cf.ui.row(gap="6"):
        with cf.ui.card(title="Zero Boilerplate", subtitle="Just Python"):
            cf.ui.text("Edit this file, save - UI updates instantly with no reload.")
            cf.ui.text("No HTML, CSS, or JS for the vast majority of apps.")
            cf.ui.divider(classes="my-3")
            cf.ui.select("Priority", ["Low","Med","High"], on_change=on_prio)
            cf.ui.divider(classes="my-3")
            cf.ui.button("Click me", variant="primary", on_click=increment)
            cf.ui.badge("LIVE", variant="success", classes="ml-2")

        with cf.ui.card(title="Production Ready", subtitle="FastAPI + WS"):
            cf.ui.text("Real routing (@app.page / + /dashboard), theming, @app.api, auth+DB built-in.")
            cf.ui.text("Use get_session_state + on_change + .refresh() for state.")

    cf.ui.footer("Made with ClayForge - MIT - Pure Python - 2026")

    # Optional (uncomment after: pip install "clayforge[auth,db]"):
    # from clayforge import auth, db
    # @app.page("/protected")
    # @auth.require_login
    # def protected(user=None): ...

    # Grok (uncomment after pip install "clayforge[grok]"):
    # from clayforge.grok import GrokChat, AgentCanvas
    # GrokChat(api_key=...) ; AgentCanvas(...)

    # Multi-page using the core page registry (see pages/ dir created by `clayforge new`).
    # For split files: create pages/foo.py with @app.page or from clayforge import page; @page
    # then `import pages.foo` from app.py to register. Shared state via imports or closure.
    # This template keeps demo in one file for simplicity; /dashboard below is real.


@app.page("/dashboard")
def dashboard():
    """Clean second page registered on the same App. Uses same core @app.page."""
    cf.ui.title("Dashboard Page")
    cf.ui.subtitle("Multi-page navigation via paths (e.g. visit /dashboard).")

    with cf.ui.card(title="pages/ + registry pattern"):
        cf.ui.text("Organize with pages/home.py + pages/dashboard.py + imports.")
        cf.ui.text("See examples/auth_db_todo.py ( / and /dashboard with auth).")
        cf.ui.text("Core: just multiple decorators on the App or default_app.")

    cf.ui.footer("ClayForge • multi-page core demo")


if __name__ == "__main__":
    app.run()
'''


def _get_minimal_app_template() -> str:
    """Absolute smallest working starter for --template minimal (still beautiful + fully live)."""
    return '''"""
Minimal ClayForge app (via `clayforge new --template minimal`).

Run:
    clayforge run
    # or: python app.py
"""
import clayforge as cf

app = cf.App(title="Minimal ClayForge")


@app.page("/")
def home():
    cf.ui.title("Hello from ClayForge")
    cf.ui.subtitle("Pure Python. Edit and save for live updates.")

    def ping():
        cf.ui.success("Button clicked - server roundtrip + WS update.")

    cf.ui.button("Click me", on_click=ping, variant="primary")
    cf.ui.footer("ClayForge - MIT - 2026")


if __name__ == "__main__":
    app.run()
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

    # Robust pre-mount + discovery (hardened for "new foo && run" w/o cd, subdirs, bare-page default_app).
    # - Auto-discovers single sibling project dir containing app.py
    # - Supports --app subdir:app (or bare "subdir")
    # - chdir + sys.path for import + server _auto_mount (Path("app.py")) + reload
    # - Falls back to shared default_app for "from clayforge import page; @page" style
    # - Better errors + guidance
    try:
        import importlib
        import sys

        # Resolve mod_name:attr
        if ":" in app_path:
            mod_name, attr = app_path.split(":", 1)
        else:
            mod_name, attr = app_path, "app"

        target_dir = Path.cwd()

        # Subdir support (e.g. `clayforge run --app myproj:app` or --app myproj from parent)
        if "/" in mod_name or "\\" in mod_name:
            p = Path(mod_name.replace("\\", "/"))
            if (target_dir / p / "app.py").exists():
                target_dir = (target_dir / p).resolve()
                mod_name = "app"
            elif p.suffix == ".py" and (target_dir / p).exists():
                target_dir = (target_dir / p.parent).resolve()
                mod_name = p.stem or "app"
        elif mod_name != "app" and (target_dir / mod_name).is_dir() and (target_dir / mod_name / "app.py").exists():
            target_dir = (target_dir / mod_name).resolve()
            mod_name = "app"

        # Default "app:app" auto-discovery for new-without-cd UX (unambiguous single subdir wins)
        if mod_name == "app" and not (target_dir / "app.py").exists():
            candidates = [
                d
                for d in target_dir.iterdir()
                if d.is_dir() and not d.name.startswith((".", "_")) and (d / "app.py").exists()
            ]
            if len(candidates) == 1:
                target_dir = candidates[0].resolve()
                console.print(f"[dim]Auto-discovered project '{target_dir.name}' (no cd needed)[/dim]")

        # Make target importable + chdir so server auto-mount + uvicorn reload_dirs + bare Path checks succeed
        if str(target_dir) not in sys.path:
            sys.path.insert(0, str(target_dir))
        if target_dir != Path.cwd():
            os.chdir(target_dir)

        mod = importlib.import_module(mod_name)
        user_app = getattr(mod, attr, None)

        from clayforge.core.app import App as _App
        from clayforge.core.server import set_current_app as _set_app

        if isinstance(user_app, _App):
            _set_app(user_app)
            os.environ["CLAYFORGE_APP"] = f"{mod_name}:{attr}"
        else:
            # bare-page support (module-level `page` decorator populates shared default_app)
            try:
                from clayforge.core.app import default_app as _def_app
                if isinstance(_def_app, _App) and getattr(_def_app, "_pages", None):
                    _set_app(_def_app)
                    os.environ.setdefault("CLAYFORGE_APP", f"{mod_name}:{attr}")
            except Exception:
                pass
    except Exception as exc:  # noqa: BLE001
        console.print(
            f"[yellow]Warning:[/yellow] Could not pre-mount {app_path}: {exc}\n"
            "Guidance:\n"
            "  • cd <project> && clayforge run   (or run from inside)\n"
            "  • clayforge run --app myproject:app   (subdir support)\n"
            "  • PYTHONPATH=theprojectdir clayforge run\n"
            "  • Bare @page style supported (no `app = App()` needed)\n"
            "Port tip: --port 8001 if busy. Kill prior py processes on Windows if bind errors."
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
    template = None
    try:
        # Preferred: read from the installed package (works after plain pip install)
        import importlib.resources as pkg_resources
        template = (pkg_resources.files("clayforge") / "showcase_demo.py").read_text(encoding="utf-8")
    except Exception:
        pass
    if not template:
        # Dev / fallback: read the one at the repo root when running from source
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
        console.print("[yellow]Note:[/yellow] Could not locate showcase_demo.py template to write local copy.")
        console.print("The server will still run the full rich demo from the package.")

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
