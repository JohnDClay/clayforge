"""ClayForge Deploy — production template helpers.

Provides ready-to-copy, production-oriented deployment files for common
platforms. Used by `clayforge deploy` and also importable for advanced use.

Templates live as real files under templates/ so they are easy to inspect
on GitHub and in installed packages.
"""

from __future__ import annotations

from collections.abc import Iterable
from importlib.resources import files
from pathlib import Path
from typing import Optional  # noqa: F401  (used in type annotations)

_TEMPLATES_DIR = files(__package__) / "templates"


def list_available_templates() -> list[str]:
    """Return filenames of all packaged deploy templates."""
    if _TEMPLATES_DIR.is_dir():
        return sorted(p.name for p in _TEMPLATES_DIR.iterdir() if p.is_file())
    return []


def get_template_content(filename: str) -> str:
    """Return the full text content of a named template."""
    if not filename or "/" in filename or "\\" in filename:
        raise ValueError("Invalid template filename")
    try:
        resource = _TEMPLATES_DIR / filename
        return resource.read_text(encoding="utf-8")
    except Exception as exc:
        raise FileNotFoundError(
            f"Template '{filename}' not found in ClayForge deploy templates. "
            f"Available: {list_available_templates()}"
        ) from exc


def write_templates(
    dest_dir: Path | str,
    *,
    filenames: Iterable[str] | None = None,
    overwrite: bool = False,
) -> list[Path]:
    """Write selected (or all) templates into dest_dir.

    Returns list of written file paths.
    """
    dest = Path(dest_dir).resolve()
    dest.mkdir(parents=True, exist_ok=True)

    available = set(list_available_templates())
    to_write = set(filenames) if filenames is not None else available

    unknown = to_write - available
    if unknown:
        raise ValueError(f"Unknown template(s): {sorted(unknown)}. Valid: {sorted(available)}")

    written: list[Path] = []
    for name in sorted(to_write):
        target = dest / name
        if target.exists() and not overwrite:
            continue
        content = get_template_content(name)
        target.write_text(content, encoding="utf-8")
        written.append(target)

    return written
