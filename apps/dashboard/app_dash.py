import dash
from dash import dcc, html
import plotly.express as px
import requests
import pandas as pd

API_URL = "http://api_service:8000/api"  # Fixed service name to match docker-compose

app = dash.Dash(__name__, requests_pathname_prefix='/dashboard/')

def get_data():
    try:
        resp = requests.get(f"{API_URL}/transactions?limit=50", timeout=10)
        resp.raise_for_status()
        return pd.DataFrame(resp.json())
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=["iface", "status", "amount", "ts"])

def layout():
    df = get_data()
    
    if df.empty:
        fig = px.bar(title="No data available")
    else:
        fig = px.histogram(df, x="iface", color="status", barmode="group")

    return html.Div([
        html.H1("Supervision Monétique"),
        dcc.Graph(figure=fig),
        dcc.Interval(id="refresh", interval=5000, n_intervals=0)  # refresh auto
    ])

app.layout = layout

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501, debug=True)
