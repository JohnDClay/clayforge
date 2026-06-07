"""
ClayForge Example 02 — Interactive Dashboard (Real Components + Events)

Demonstrates everything that works *today* after the rendering milestone:
- Full layout with row + nested cards
- Real buttons with server-side on_click handlers
- ui.badge, ui.divider, ui.text_input
- Live updates (the handlers can mutate state and we can trigger re-renders in follow-ups)
- Professional, production-ready visual quality with zero styling code

Run:
    python examples/02_interactive_dashboard.py
    # or after `clayforge new`
    clayforge run --app examples.02_interactive_dashboard:app
"""

import clayforge as cf

app = cf.App(title="ClayForge • Interactive Dashboard", theme="dark")

# Simple in-memory "database" for the demo (real apps would use a proper store)
METRICS = {"users": 1248, "revenue": 48290, "conversion": 3.4}


@app.page("/")
def dashboard():
    cf.ui.title("Live Dashboard")
    cf.ui.subtitle("Everything here is real Python components + server event handlers")

    with cf.ui.row(gap="6"):
        # KPI Cards
        with cf.ui.card(title="Active Users", subtitle="Last 30 days"):
            cf.ui.text(str(METRICS["users"]), size="2xl")
            cf.ui.badge("↑ 12%", variant="success")

        with cf.ui.card(title="Revenue", subtitle="MRR"):
            cf.ui.text(f"${METRICS['revenue']:,}", size="2xl")
            cf.ui.badge("↑ 8%", variant="success")

        with cf.ui.card(title="Conversion", subtitle="This week"):
            cf.ui.text(f"{METRICS['conversion']}%", size="2xl")
            cf.ui.badge("↓ 0.3%", variant="warning")

    cf.ui.divider()

    with cf.ui.row(gap="6"):
        with cf.ui.card(
            title="Quick Actions", subtitle="Click the buttons — handlers run on the server"
        ):

            def bump_users():
                METRICS["users"] += 17
                print(f"[Dashboard] Users bumped to {METRICS['users']}")
                # In a future iteration we will have ui.refreshable or targeted re-render
                # For now the print + toast proves the full roundtrip works

            cf.ui.button("Simulate new signup (+17 users)", on_click=bump_users, variant="primary")

            def simulate_sale():
                METRICS["revenue"] += 1290
                print(f"[Dashboard] Revenue now ${METRICS['revenue']:,}")

            cf.ui.button("Log a big sale (+$1,290)", on_click=simulate_sale, variant="secondary")

            cf.ui.divider()

            name = cf.ui.text_input("Customer name", placeholder="Acme Corp", value="New Lead")
            if cf.ui.button("Add lead", variant="ghost"):
                print(f"[Dashboard] Would add lead: {name}")

        with cf.ui.card(title="System Status"):
            cf.ui.badge("All systems operational", variant="success")
            cf.ui.text("Last incident: 11 days ago")
            cf.ui.text("Uptime: 99.98%")
            cf.ui.markdown("WebSocket latency: < 20ms<br>Active connections: 4")

    cf.ui.footer("Example 02 • Real components • Real event handlers • Zero boilerplate")


if __name__ == "__main__":
    app.run()
