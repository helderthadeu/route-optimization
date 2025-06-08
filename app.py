"""
Dash Application for Subway Route Planning in Manhattan

This application calculates the shortest subway route between two stations
using Floyd-Warshall algorithm results, and displays the route on a map with 
details like next train arrival and travel time.
"""

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from src.floyd_utils import load_vertices, load_predecessors, get_short_path
from src.next_train import next_train_time
from src.floyd_warshall.floyd_warshall import generate_floyd_warshall
import os

# Load subway graph data
vertices = load_vertices("src/files/vertices.txt")
predecessors = load_predecessors("src/files/predecessors.txt", vertices)

# Initialize Dash application
app = dash.Dash(__name__)

# Generate dropdown options for station selection
station_options = [{'label': f"{v.station_name} ({v.line})", 'value': v.id} for v in vertices]

# Define application layout
app.layout = html.Div([
    html.H1("Busca de Rotas"),  # Route search title
    html.P("Busca de melhores rotas de metrô em Manhattan - Nova York"),  # Description
    html.H3("Enzo, Gabriel e Helder - Engenharia de Computação"),  # Authors

    html.Div(style={"display": "flex"}, children=[
        # Left side: dropdowns and button
        html.Div([
            html.H2("Busca de rotas: ", id="busca-title"),
            
            html.Label("Origem"),  # Origin station
            dcc.Dropdown(
                id="origin",
                options=station_options,
                placeholder="Selecione a estação de origem",
                style={"marginBottom": "10px", "width": "100%"}
            ),

            html.Label("Destino"),  # Destination station
            dcc.Dropdown(
                id="destination",
                options=station_options,
                placeholder="Selecione a estação de destino",
                style={"width": "100%"}
            ),

            html.Div(style={"marginTop": "20px"}, children=[
                html.Button("Calcular rota", id="botao-calcular", n_clicks=0)
            ]),

            html.Div(id="info-rota"),  # Displays route info
            html.Div(id="saida-proximo-trem"),  # Displays next train info
        ], id="left-section"),

        # Right side: route map
        html.Div([
            dcc.Graph(id="mapa-rota")
        ], id="right-section")
    ]),
    html.Footer("Pontifícia Universidade Católica de Minas Gerais - 2025")  # Footer
])

@app.callback(
    [Output("mapa-rota", "figure"),
     Output("info-rota", "children"),
     Output("saida-proximo-trem", "children")],
    [Input("botao-calcular", "n_clicks")],
    [dash.State("origin", "value"),
     dash.State("destination", "value")]
)
def update_mapa(n_clicks, orig_id, dest_id):
    """
    Callback function to update the map and route information
    based on selected origin and destination stations.

    Parameters:
    - n_clicks (int): Number of button clicks
    - orig_id (str): Origin station ID
    - dest_id (str): Destination station ID

    Returns:
    - fig (plotly.graph_objs.Figure): Map with route plotted
    - info_text (str): Summary of the route
    - proximo_trem_text (str): Estimated arrival time at destination
    """
    if not n_clicks or orig_id is None or dest_id is None or orig_id == dest_id:
        return go.Figure(), "", ""

    # Retrieve origin and destination vertex objects
    orig = next(v for v in vertices if v.id == orig_id)
    dest = next(v for v in vertices if v.id == dest_id)

    # Find the shortest path between origin and destination
    path = get_short_path(vertices, predecessors, orig, dest)
    if not path:
        return go.Figure(), "Nenhuma rota encontrada.", ""

    # Calculate total travel time (default weight = 2 if not defined)
    time_travel = sum(getattr(path[i], 'weight', 2) for i in range(len(path)-1))
    time_travel_hours = time_travel / 60.0

    # Get next train time based on origin station and current time
    now = datetime.now().time()
    next_train = next_train_time(orig.line, orig.station_name, now, time_travel_hours)

    # Extract latitude, longitude, and station names for the map
    lats = [p.lat for p in path]
    lons = [p.lon for p in path]
    names = [f"{p.station_name} ({p.line})" for p in path]

    # Plot route on map using Plotly
    fig = go.Figure(go.Scattermapbox(
        mode="markers+lines",
        lat=lats,
        lon=lons,
        marker={'size': 10, 'color': "#00AD54"},  # Green markers
        text=names,
        line=dict(width=3, color='blue')  # Blue path line
    ))
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=12,
        mapbox_center={"lat": float(path[0].lat), "lon": float(path[0].lon)},
        margin={"r":0, "t":0, "l":0, "b":0}
    )

    # Format informational texts
    info_text = f"Rota de {orig.station_name} até {dest.station_name} com {len(path)-1} conexões."
    proximo_trem_text = f"Chegada à {dest.station_name} às {next_train.strftime('%H:%M:%S')}, saindo agora."

    return fig, info_text, proximo_trem_text

if __name__ == "__main__":
    """
    Entry point of the application.
    If Floyd-Warshall results do not exist, it generates them.
    Then runs the Dash app.
    """
    if not (os.path.exists("src/files/predecessors.txt") and os.path.exists("src/files/floyd_washal_lenght.txt")):
        generate_floyd_warshall()

    app.run(debug=True)
