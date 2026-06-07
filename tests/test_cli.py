"""Minimal pytest coverage for core CLI commands after gallery removal (showcase is the demo surface)."""

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
