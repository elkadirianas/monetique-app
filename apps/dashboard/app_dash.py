import dash
from dash import dcc, html, Output, Input, dash_table
import plotly.express as px
import plotly.graph_objects as go
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

# ---------- Enhanced Figures ----------
def transactions_by_iface(df):
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False, font_size=16)
        fig.update_layout(
            title="Transactions by Interface & Status",
            template="plotly_white",
            height=350
        )
        return fig
    
    fig = px.histogram(
        df, x="iface", color="status", barmode="group",
        title="Transactions by Interface & Status",
        color_discrete_map={
            'success': '#10B981',
            'failed': '#EF4444', 
            'pending': '#F59E0B',
            'cancelled': '#6B7280'
        }
    )
    fig.update_layout(
        template="plotly_white",
        title_font_size=16,
        title_font_color="#1F2937",
        height=350,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    return fig

def amount_by_iface(df):
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False, font_size=16)
        fig.update_layout(
            title="Total Amount by Interface",
            template="plotly_white",
            height=350
        )
        return fig
    
    agg = df.groupby("iface", as_index=False)["amount"].sum()
    fig = px.bar(
        agg, x="iface", y="amount", text_auto=True,
        title="Total Amount by Interface"
    )
    fig.update_traces(marker_color='#3B82F6', textposition='outside')
    fig.update_layout(
        template="plotly_white",
        title_font_size=16,
        title_font_color="#1F2937",
        height=350,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    return fig

def status_distribution(df):
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False, font_size=16)
        fig.update_layout(
            title="Status Distribution",
            template="plotly_white",
            height=350
        )
        return fig
    
    fig = px.pie(
        df, names="status", title="Status Distribution",
        hole=0.4,
        color_discrete_map={
            'success': '#10B981',
            'failed': '#EF4444', 
            'pending': '#F59E0B',
            'cancelled': '#6B7280'
        }
    )
    fig.update_layout(
        template="plotly_white",
        title_font_size=16,
        title_font_color="#1F2937",
        height=350,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    return fig

def get_metrics(df):
    if df.empty:
        return {"total": 0, "success_rate": 0, "total_amount": 0, "avg_amount": 0}
    
    total = len(df)
    success_count = len(df[df['status'] == 'success']) if 'status' in df.columns else 0
    success_rate = (success_count / total * 100) if total > 0 else 0
    total_amount = df['amount'].sum() if 'amount' in df.columns else 0
    avg_amount = df['amount'].mean() if 'amount' in df.columns and total > 0 else 0
    
    return {
        "total": total,
        "success_rate": success_rate,
        "total_amount": total_amount,
        "avg_amount": avg_amount
    }

# ---------- Enhanced Layout ----------
app.layout = html.Div(
    style={
        "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "backgroundColor": "#F8FAFC",
        "minHeight": "100vh",
        "margin": "0",
        "padding": "0"
    },
    children=[
        # Header
        html.Div(
            style={
                "backgroundColor": "#FFFFFF",
                "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
                "padding": "24px 32px",
                "marginBottom": "32px"
            },
            children=[
                html.H1(
                    "💳 Supervision Monétique",
                    style={
                        "margin": "0",
                        "fontSize": "32px",
                        "fontWeight": "700",
                        "color": "#1F2937",
                        "textAlign": "center"
                    }
                ),
                html.P(
                    "Real-time payment monitoring dashboard",
                    style={
                        "margin": "8px 0 0 0",
                        "fontSize": "16px",
                        "color": "#6B7280",
                        "textAlign": "center"
                    }
                )
            ]
        ),

        # Auto-refresh interval
        dcc.Interval(id="refresh", interval=8000, n_intervals=0),

        # Main content container
        html.Div(
            style={"maxWidth": "1400px", "margin": "0 auto", "padding": "0 32px"},
            children=[
                # Metrics Cards
                html.Div(
                    id="metrics-container",
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
                        "gap": "24px",
                        "marginBottom": "32px"
                    }
                ),

                # Charts Row 1
                html.Div([
                    html.Div([
                        html.Div(
                            dcc.Graph(id="graph-status-dist", style={"height": "350px"}),
                            style={
                                "backgroundColor": "#FFFFFF",
                                "borderRadius": "12px",
                                "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
                                "padding": "20px"
                            }
                        )
                    ], style={"width": "48%", "display": "inline-block", "marginRight": "4%"}),

                    html.Div([
                        html.Div(
                            dcc.Graph(id="graph-amount", style={"height": "350px"}),
                            style={
                                "backgroundColor": "#FFFFFF",
                                "borderRadius": "12px",
                                "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
                                "padding": "20px"
                            }
                        )
                    ], style={"width": "48%", "display": "inline-block"}),
                ], style={"marginBottom": "32px"}),

                # Charts Row 2
                html.Div([
                    html.Div(
                        dcc.Graph(id="graph-transactions", style={"height": "400px"}),
                        style={
                            "backgroundColor": "#FFFFFF",
                            "borderRadius": "12px",
                            "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
                            "padding": "20px"
                        }
                    )
                ], style={"marginBottom": "32px"}),

                # Data Table Section
                html.Div([
                    html.H3(
                        "📋 Recent Transactions",
                        style={
                            "fontSize": "24px",
                            "fontWeight": "600",
                            "color": "#1F2937",
                            "marginBottom": "20px"
                        }
                    ),
                    html.Div(
                        dash_table.DataTable(
                            id="transactions-table",
                            columns=[
                                {"name": "Interface", "id": "iface"},
                                {"name": "Status", "id": "status"},
                                {"name": "Amount", "id": "amount", "type": "numeric", "format": {"specifier": ".2f"}},
                                {"name": "Timestamp", "id": "ts"},
                            ],
                            data=[],
                            page_size=15,
                            style_table={
                                "overflowX": "auto",
                                "borderRadius": "8px",
                                "overflow": "hidden"
                            },
                            style_cell={
                                "padding": "12px 16px",
                                "textAlign": "left",
                                "fontSize": "14px",
                                "fontFamily": "'Inter', sans-serif",
                                "border": "none",
                                "borderBottom": "1px solid #E5E7EB"
                            },
                            style_header={
                                "backgroundColor": "#F9FAFB",
                                "color": "#374151",
                                "fontWeight": "600",
                                "fontSize": "14px",
                                "textTransform": "uppercase",
                                "letterSpacing": "0.05em",
                                "border": "none",
                                "borderBottom": "2px solid #E5E7EB"
                            },
                            style_data_conditional=[
                                {
                                    'if': {'filter_query': '{status} = success'},
                                    'backgroundColor': '#F0FDF4',
                                    'color': '#166534',
                                },
                                {
                                    'if': {'filter_query': '{status} = failed'},
                                    'backgroundColor': '#FEF2F2',
                                    'color': '#991B1B',
                                },
                                {
                                    'if': {'filter_query': '{status} = pending'},
                                    'backgroundColor': '#FFFBEB',
                                    'color': '#92400E',
                                }
                            ]
                        ),
                        style={
                            "backgroundColor": "#FFFFFF",
                            "borderRadius": "12px",
                            "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
                            "padding": "20px"
                        }
                    )
                ])
            ]
        )
    ]
)

# ---------- Enhanced Callbacks ----------
@app.callback(
    [Output("graph-transactions", "figure"),
     Output("graph-amount", "figure"),
     Output("graph-status-dist", "figure"),
     Output("transactions-table", "data"),
     Output("metrics-container", "children")],
    Input("refresh", "n_intervals")
)
def update_dashboard(n):
    df = get_data(limit=100)
    metrics = get_metrics(df)
    
    # Create metrics cards
    metrics_cards = [
        html.Div([
            html.Div([
                html.H3(f"{metrics['total']:,}", style={"margin": "0", "fontSize": "28px", "fontWeight": "700", "color": "#1F2937"}),
                html.P("Total Transactions", style={"margin": "4px 0 0 0", "fontSize": "14px", "color": "#6B7280", "fontWeight": "500"})
            ], style={"textAlign": "center"})
        ], style={
            "backgroundColor": "#FFFFFF",
            "borderRadius": "12px",
            "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
            "padding": "24px",
            "borderLeft": "4px solid #3B82F6"
        }),
        
        html.Div([
            html.Div([
                html.H3(f"{metrics['success_rate']:.1f}%", style={"margin": "0", "fontSize": "28px", "fontWeight": "700", "color": "#10B981"}),
                html.P("Success Rate", style={"margin": "4px 0 0 0", "fontSize": "14px", "color": "#6B7280", "fontWeight": "500"})
            ], style={"textAlign": "center"})
        ], style={
            "backgroundColor": "#FFFFFF",
            "borderRadius": "12px",
            "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
            "padding": "24px",
            "borderLeft": "4px solid #10B981"
        }),
        
        html.Div([
            html.Div([
                html.H3(f"€{metrics['total_amount']:,.2f}", style={"margin": "0", "fontSize": "28px", "fontWeight": "700", "color": "#1F2937"}),
                html.P("Total Amount", style={"margin": "4px 0 0 0", "fontSize": "14px", "color": "#6B7280", "fontWeight": "500"})
            ], style={"textAlign": "center"})
        ], style={
            "backgroundColor": "#FFFFFF",
            "borderRadius": "12px",
            "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
            "padding": "24px",
            "borderLeft": "4px solid #F59E0B"
        }),
        
        html.Div([
            html.Div([
                html.H3(f"€{metrics['avg_amount']:.2f}", style={"margin": "0", "fontSize": "28px", "fontWeight": "700", "color": "#1F2937"}),
                html.P("Average Amount", style={"margin": "4px 0 0 0", "fontSize": "14px", "color": "#6B7280", "fontWeight": "500"})
            ], style={"textAlign": "center"})
        ], style={
            "backgroundColor": "#FFFFFF",
            "borderRadius": "12px",
            "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
            "padding": "24px",
            "borderLeft": "4px solid #8B5CF6"
        })
    ]
    
    return (
        transactions_by_iface(df),
        amount_by_iface(df),
        status_distribution(df),
        df.to_dict("records"),
        metrics_cards
    )

# ---------- Startup ----------
if not check_connectivity():
    print("⚠️ Warning: API not reachable at startup.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501, debug=True)