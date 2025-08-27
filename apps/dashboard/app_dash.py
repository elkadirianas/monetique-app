import dash
from dash import dcc, html, Output, Input, dash_table
import plotly.express as px
import requests
import pandas as pd

API_URL = "http://api_service:8000/api"  # Fixed service name to match docker-compose

external_stylesheets = [
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css",
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap",
]

app = dash.Dash(
    __name__,
    requests_pathname_prefix='/dashboard/',
    title="Supervision Monétique",
    external_stylesheets=external_stylesheets,
)


# ---------- Data ----------
def get_data(limit: int = 100) -> pd.DataFrame:
    try:
        resp = requests.get(f"{API_URL}/transactions?limit={limit}", timeout=10)
        resp.raise_for_status()
        return pd.DataFrame(resp.json())
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=["iface", "status", "amount", "ts"])


# ---------- Figures ----------
def transactions_by_iface(df: pd.DataFrame, template: str):
    if df.empty:
        fig = px.bar(title="No data available")
    else:
        fig = px.histogram(
            df,
            x="iface",
            color="status",
            barmode="group",
            title="Transactions by Interface & Status",
        )
    fig.update_layout(template=template, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def amount_by_iface(df: pd.DataFrame, template: str):
    if df.empty:
        fig = px.bar(title="No data available")
    else:
        agg = df.groupby("iface", as_index=False)["amount"].sum()
        fig = px.bar(
            agg,
            x="iface",
            y="amount",
            text_auto=True,
            title="Total Amount by Interface",
        )
    fig.update_layout(template=template, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def status_distribution(df: pd.DataFrame, template: str):
    if df.empty:
        fig = px.pie(title="No data available")
    else:
        fig = px.pie(df, names="status", hole=0.45, title="Status Distribution")
    fig.update_layout(template=template, margin=dict(l=10, r=10, t=50, b=10))
    return fig


# ---------- KPI Helpers ----------
def compute_kpis(df: pd.DataFrame):
    total_count = int(len(df)) if not df.empty else 0
    total_amount = float(df["amount"].sum()) if (not df.empty and "amount" in df) else 0.0
    if df.empty or "status" not in df:
        success_rate = 0.0
    else:
        success_like = {"success", "approved", "ok", "completed"}
        statuses = df["status"].astype(str).str.lower()
        successes = statuses.isin(success_like).sum()
        success_rate = (successes / max(total_count, 1)) * 100.0
    return total_count, total_amount, success_rate


# ---------- Layout ----------
HEADER_STYLE_LIGHT = {
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "space-between",
    "padding": "16px 20px",
    "borderRadius": "12px",
    "background": "linear-gradient(135deg, #e6f0ff 0%, #f6f9ff 100%)",
    "border": "1px solid #dbe6ff",
}

HEADER_STYLE_DARK = {
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "space-between",
    "padding": "16px 20px",
    "borderRadius": "12px",
    "background": "linear-gradient(135deg, #0b1a33 0%, #0f213f 100%)",
    "border": "1px solid #0f2a52",
}

CARD_STYLE = {
    "border": "1px solid rgba(0,0,0,0.06)",
    "borderRadius": "12px",
    "padding": "14px",
    "boxShadow": "0 2px 12px rgba(0,0,0,0.06)",
    "backgroundColor": "white",
}

CARD_STYLE_DARK = {
    "border": "1px solid rgba(255,255,255,0.08)",
    "borderRadius": "12px",
    "padding": "14px",
    "boxShadow": "0 2px 12px rgba(0,0,0,0.35)",
    "backgroundColor": "#15233b",
}

app.layout = html.Div(
    id="page",
    style={
        "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Oxygen, Ubuntu, Cantarell, \"Fira Sans\", \"Droid Sans\", \"Helvetica Neue\", Arial, \"Noto Sans\", sans-serif",
        "backgroundColor": "#f7f9fc",
        "minHeight": "100vh",
        "padding": "22px",
    },
    children=[
        html.Div(
            id="header",
            style=HEADER_STYLE_LIGHT,
            children=[
                html.Div([
                    html.H2("💳 Supervision Monétique", style={"margin": 0, "color": "#0b3d91", "fontWeight": 700}),
                    html.Div("Live monitoring of transactions and status", style={"color": "#335caa", "fontSize": "14px"}),
                ]),
                html.Div([
                    html.Label("Theme", htmlFor="theme-toggle", style={"marginRight": "8px", "fontWeight": 600}),
                    dcc.RadioItems(
                        id="theme-toggle",
                        options=[
                            {"label": "Light", "value": "light"},
                            {"label": "Dark", "value": "dark"},
                        ],
                        value="light",
                        labelStyle={"display": "inline-block", "marginRight": "12px"},
                        inputStyle={"marginRight": "6px"},
                    ),
                ])
            ],
        ),

        dcc.Interval(id="refresh", interval=8000, n_intervals=0),

        html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(3, 1fr)", "gap": "12px", "marginTop": "18px"},
            children=[
                html.Div(id="kpi-total", style={**CARD_STYLE, "minHeight": "84px"}),
                html.Div(id="kpi-amount", style={**CARD_STYLE, "minHeight": "84px"}),
                html.Div(id="kpi-success", style={**CARD_STYLE, "minHeight": "84px"}),
            ],
        ),

        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px", "marginTop": "12px"},
            children=[
                html.Div(children=[dcc.Graph(id="graph-status-dist", style={"height": "360px"})], style=CARD_STYLE),
                html.Div(children=[dcc.Graph(id="graph-amount", style={"height": "360px"})], style=CARD_STYLE),
            ],
        ),

        html.Div(style={"marginTop": "12px"}, children=[
            html.Div(children=[dcc.Graph(id="graph-transactions", style={"height": "420px"})], style=CARD_STYLE),
        ]),

        html.Div(style={"marginTop": "14px"}, children=[
            html.H4("📋 Transactions", style={"marginBottom": "8px", "color": "#0b3d91"}),
            html.Div(style=CARD_STYLE, children=[
                dash_table.DataTable(
                    id="transactions-table",
                    columns=[
                        {"name": "iface", "id": "iface"},
                        {"name": "status", "id": "status"},
                        {"name": "amount", "id": "amount"},
                        {"name": "ts", "id": "ts"},
                    ],
                    data=[],
                    page_size=10,
                    style_table={"overflowX": "auto"},
                    style_cell={"padding": "8px", "textAlign": "left", "border": "none"},
                    style_header={
                        "backgroundColor": "#0b3d91",
                        "color": "white",
                        "fontWeight": "700",
                        "border": "none",
                    },
                    style_data_conditional=[
                        {
                            "if": {"filter_query": "lower({status}) = 'success'"},
                            "color": "#0f5132",
                            "backgroundColor": "#d1e7dd",
                        },
                        {
                            "if": {"filter_query": "lower({status}) = 'failed' || lower({status}) = 'error'"},
                            "color": "#842029",
                            "backgroundColor": "#f8d7da",
                        },
                        {
                            "if": {"filter_query": "lower({status}) = 'pending' || lower({status}) = 'processing'"},
                            "color": "#664d03",
                            "backgroundColor": "#fff3cd",
                        },
                    ],
                )
            ]),
        ]),
    ],
)


# ---------- Callbacks ----------
@app.callback(
    [
        Output("graph-transactions", "figure"),
        Output("graph-amount", "figure"),
        Output("graph-status-dist", "figure"),
        Output("transactions-table", "data"),
        Output("kpi-total", "children"),
        Output("kpi-amount", "children"),
        Output("kpi-success", "children"),
        Output("page", "style"),
        Output("header", "style"),
    ],
    [Input("refresh", "n_intervals"), Input("theme-toggle", "value")],
)
def update_dashboard(n, theme):
    df = get_data(limit=100)

    template = "plotly_dark" if theme == "dark" else "plotly_white"

    fig_transactions = transactions_by_iface(df, template)
    fig_amount = amount_by_iface(df, template)
    fig_status = status_distribution(df, template)

    total_count, total_amount, success_rate = compute_kpis(df)

    kpi_total = html.Div([
        html.Div("Total Transactions", style={"fontSize": "13px", "color": "#6c757d"}),
        html.Div(f"{total_count:,}", style={"fontSize": "26px", "fontWeight": 700}),
    ])

    kpi_amount = html.Div([
        html.Div("Total Amount", style={"fontSize": "13px", "color": "#6c757d"}),
        html.Div(f"{total_amount:,.2f}", style={"fontSize": "26px", "fontWeight": 700}),
    ])

    kpi_success = html.Div([
        html.Div("Success Rate", style={"fontSize": "13px", "color": "#6c757d"}),
        html.Div(f"{success_rate:.1f}%", style={"fontSize": "26px", "fontWeight": 700}),
    ])

    light_page_style = {
        "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Oxygen, Ubuntu, Cantarell, \"Fira Sans\", \"Droid Sans\", \"Helvetica Neue\", Arial, \"Noto Sans\", sans-serif",
        "backgroundColor": "#f7f9fc",
        "minHeight": "100vh",
        "padding": "22px",
        "color": "#1b2a4a",
    }

    dark_page_style = {
        "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Oxygen, Ubuntu, Cantarell, \"Fira Sans\", \"Droid Sans\", \"Helvetica Neue\", Arial, \"Noto Sans\", sans-serif",
        "backgroundColor": "#0b172b",
        "minHeight": "100vh",
        "padding": "22px",
        "color": "#e2e8f0",
    }

    page_style = dark_page_style if theme == "dark" else light_page_style
    header_style = HEADER_STYLE_DARK if theme == "dark" else HEADER_STYLE_LIGHT

    return (
        fig_transactions,
        fig_amount,
        fig_status,
        df.to_dict("records"),
        kpi_total,
        kpi_amount,
        kpi_success,
        page_style,
        header_style,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501, debug=True)
