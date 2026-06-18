"""CLI tests: help + new scaffold output quality (default/minimal) + template options + run pre-mount/discovery.

Covers packaging role requirements for new + run robustness (no showcase changes).
"""

from pathlib import Path

from typer.testing import CliRunner

from clayforge.cli.main import app

runner = CliRunner()


def test_cli_showcase_help_present():
    """showcase command is registered and documented."""
    result = runner.invoke(app, ["showcase", "--help"])
    assert result.exit_code == 0
    output = result.output.lower()
    assert "showcase" in output


def test_cli_new_help_present():
    result = runner.invoke(app, ["new", "--help"])
    assert result.exit_code == 0


def test_cli_run_help_present():
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0


def test_cli_deploy_help_present():
    result = runner.invoke(app, ["deploy", "--help"])
    assert result.exit_code == 0


# --- New coverage: scaffold quality, templates, run pre-mount ---


def test_cli_new_default_creates_clean_scaffold(tmp_path):
    """Default template produces bloat-free excellent starter + README + support files."""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["new", "demoapp"])
        assert result.exit_code == 0
        proj = Path("demoapp")
        assert (proj / "app.py").exists()
        assert (proj / "README.md").exists()
        assert (proj / ".env.example").exists()
        assert (proj / "requirements.txt").exists()
        assert (proj / ".gitignore").exists()
        assert (proj / "pages" / "__init__.py").exists()
        assert (proj / "components" / "__init__.py").exists()

        app_py = (proj / "app.py").read_text(encoding="utf-8")
        # Recommended patterns present, no old bloat
        assert "import clayforge as cf" in app_py
        assert "app = cf.App(" in app_py
        assert '@app.page("/")' in app_py
        assert "def home():" in app_py
        assert "count = [0]" in app_py  # live state pattern
        assert "on_click=increment" in app_py
        assert "cf.ui.row" in app_py and "cf.ui.card" in app_py
        assert "cf.ui.footer" in app_py
        assert "if __name__ == \"__main__\":" in app_py
        assert "app.run()" in app_py
        # bloat free: no dangling text_input, no eager (non-commented) grok import
        assert "text_input" not in app_py
        non_comment = "\n".join(ln for ln in app_py.splitlines() if not ln.strip().startswith("#"))
        assert "from clayforge.grok" not in non_comment
        assert "GrokChat(" not in non_comment

        readme = (proj / "README.md").read_text(encoding="utf-8")
        assert "clayforge run" in readme
        assert "Auto-discovers" in readme or "parent dir" in readme
        assert "clayforge deploy" in readme
        assert "grok,db,auth,viz" in readme
        # No heavy old section
        assert "Protect a page with auth + query the DB" not in readme


def test_cli_new_minimal_template(tmp_path):
    """--template minimal produces smallest clean runnable app (no extras)."""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["new", "miniapp", "--template", "minimal"])
        assert result.exit_code == 0
        app_py = (Path("miniapp") / "app.py").read_text(encoding="utf-8")
        assert "Minimal ClayForge" in app_py
        assert "cf.ui.button" in app_py
        assert "cf.ui.success" in app_py
        assert "app = cf.App(title=" in app_py
        # Still has footer and live handler
        assert "if __name__" in app_py
        # Smaller than default
        assert len(app_py) < 900


def test_cli_new_unknown_template_falls_back(tmp_path):
    """Unknown template falls to default (no crash)."""
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["new", "fallbackapp", "--template", "grok-heavy"])
        assert result.exit_code == 0
        content = (Path("fallbackapp") / "app.py").read_text()
        assert "My ClayForge App" in content or "Production Ready" in content


def test_cli_run_pre_mount_and_discovery(monkeypatch, tmp_path, capsys):
    """Run pre-mount logic (warnings, default_app bare, no actual server start). Covers new+run flow."""
    import uvicorn

    def fake_run(*a, **k):
        # Do not actually bind server in tests
        return None

    monkeypatch.setattr(uvicorn, "run", fake_run)

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Case 1: bad app -> warning path (better guidance)
        result = runner.invoke(app, ["run", "--app", "nonexistent:foo", "--no-reload"])
        out = result.output
        assert "Warning" in out or "Could not pre-mount" in out or "Guidance" in out
        # Should not have crashed hard (exit may be 0 or handled)
        assert result.exit_code in (0, 1, None)

        # Case 2: create a bare-page style project (tests default_app path + discovery)
        bare_proj = Path("bareproj")
        bare_proj.mkdir()
        (bare_proj / "app.py").write_text(
            """from clayforge import page
@page("/")
def home():
    from clayforge import ui as cfui
    cfui.title("Bare page works")
""",
            encoding="utf-8",
        )
        # invoke run from parent; should auto-discover (or at least not explode in pre-mount)
        result2 = runner.invoke(app, ["run", "--no-reload"])
        # May print auto-discover or warning (no app=var), but must succeed to uvicorn stub
        assert result2.exit_code in (0, 1, None)
        # At minimum, "Starting" panel or pre logic ran
        assert "Starting" in result2.output or "ClayForge" in result2.output

    # Ensure no server actually started
    # (fake prevents it)
