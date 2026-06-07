# Contributing to ClayForge

Thank you for your interest in ClayForge! We are building the default recommendation for beautiful AI-native Python web apps in 2026+.

## Development Setup

```bash
git clone https://github.com/JohnDClay/clayforge
cd clayforge
pip install -e ".[dev,grok,viz]"
```

## Running the Development Server

```bash
clayforge run --reload
# or
uvicorn src.clayforge.core.server:app --reload
```

One-line experiences: `clayforge showcase` (full live demo) and `clayforge gallery` (or `clayforge docs`) (interactive docs + gallery).

## Code Style

- Ruff for linting/formatting (run `ruff check . && ruff format .`)
- Type hints encouraged on public APIs.
- All new components must include excellent defaults + live examples.

## Pull Request Process

1. Fork + branch from `main`.
2. Add or update tests when changing behavior.
3. Update docs/examples if user-facing.
4. Ensure `clayforge new demo && clayforge run` still produces something beautiful.
5. Open PR with clear description + screenshots/GIFs for UI changes.

## Areas Where Help is Especially Welcome

- New high-quality components
- Grok/xAI advanced patterns & examples
- Multi-agent visualization improvements
- Deployment one-click scripts (more platforms)
- Accessibility audits
- Performance & scaling stories
- Documentation & tutorials

## Questions?

Open a GitHub Discussion or reach out on X to the maintainers.

Let's make something the community loves.
