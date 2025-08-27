import dash
from dash import dcc, html, Output, Input, dash_table
import plotly.express as px
import requests
import pandas as pd

API_URL = "http://api_service:8000/api"

app = dash.Dash(__name__, title="Supervision Monétique")
app.title = "Supervision Monétique"

# ---------- Utils ----------
def check_connectivity():
    try:
        resp = requests.get(f"{API_URL}/transactions?limit=1", timeout=3)
        resp.raise_for_status()
        print("API connectivity: OK")
        return True
    except Exception as e:
        print(f"API connectivity failed: {e}")
        return False

def get_data(limit=100):
    try:
        resp = requests.get(f"{API_URL}/transactions?limit={limit}", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data)
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame(columns=["iface", "status", "amount", "ts"])

# ---------- Figures ----------
def transactions_by_iface(df):
    if df.empty:
        return px.bar(title="No data available")
    return px.histogram(
        df, x="iface", color="status", barmode="group",
        title="Transactions by Interface & Status"
    )

def amount_by_iface(df):
    if df.empty:
        return px.bar(title="No data available")
    agg = df.groupby("iface", as_index=False)["amount"].sum()
    return px.bar(
        agg, x="iface", y="amount", text_auto=True,
        title="Total Amount by Interface"
    )

def status_distribution(df):
    if df.empty:
        return px.pie(title="No data available")
    return px.pie(
        df, names="status", title="Status Distribution",
        hole=0.4
    )

# ---------- Layout ----------
app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "backgroundColor": "#f9f9f9", "padding": "20px"},
    children=[
        html.H1("💳 Supervision Monétique", style={"textAlign": "center", "color": "#003366"}),

        dcc.Interval(id="refresh", interval=8000, n_intervals=0),

        html.Div([
            html.Div([
                dcc.Graph(id="graph-status-dist", style={"height": "350px"}),
            ], className="six columns", style={"padding": "10px"}),

            html.Div([
                dcc.Graph(id="graph-amount", style={"height": "350px"}),
            ], className="six columns", style={"padding": "10px"}),
        ], className="row"),

        html.Div([
            dcc.Graph(id="graph-transactions", style={"height": "400px"})
        ], style={"padding": "10px"}),

        html.H3("📋 Transactions Table", style={"marginTop": "30px", "color": "#003366"}),

        dash_table.DataTable(
            id="transactions-table",
            columns=[
                {"name": "iface", "id": "iface"},
                {"name": "status", "id": "status"},
                {"name": "amount", "id": "amount", "type": "numeric", "format": {"specifier": ".2f"}},
                {"name": "ts", "id": "ts"},
            ],
            data=[],
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"padding": "8px", "textAlign": "left"},
            style_header={"backgroundColor": "#003366", "color": "white", "fontWeight": "bold"},
        )
    ]
)

# ---------- Callbacks ----------
@app.callback(
    [Output("graph-transactions", "figure"),
     Output("graph-amount", "figure"),
     Output("graph-status-dist", "figure"),
     Output("transactions-table", "data")],
    Input("refresh", "n_intervals")
)
def update_dashboard(n):
    df = get_data(limit=100)
    return (
        transactions_by_iface(df),
        amount_by_iface(df),
        status_distribution(df),
        df.to_dict("records")
    )

# ---------- Startup ----------
if not check_connectivity():
    print("⚠️ Warning: API not reachable at startup.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501, debug=True)
