import dash 
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import os

from src.file_operate import *
from src.floyd_warshall.floyd_warshall import *
from src.next_train import *
from src.floyd_utils import *

def somar_horas_decimais(horas_decimais: float) -> str:
    """
    Adds the current time to a given decimal number of hours and returns the result in HH:MM format.

    Args:
        horas_decimais (float): Number of decimal hours to add (e.g., 1.5 means 1 hour and 30 minutes)

    Returns:
        str: Resulting time in HH:MM format
    """
    agora = datetime.now()
    minutos = int(horas_decimais * 60)
    nova_hora = agora + timedelta(minutes=minutos)
    return nova_hora.strftime("%H:%M")

# Load subway graph data from files
vertices = load_vertices("files/vertices.txt")
predecessors = load_predecessors("files/predecessors.txt", vertices)
length_matrix = load_length_matrix_from_file("files/floyd_washal_lenght.txt")

# Initialize Dash application
app = dash.Dash(__name__)

# Dropdown options for stations
station_options = [{'label': f"{v.station_name} ({v.line})", 'value': v.id} for v in vertices]

# Application layout
app.layout = html.Div([
    html.H1("Busca de Rotas"),
    html.P("Busca de melhores rotas de metrô em Manhattan - Nova York"),
    html.H3("Enzo, Gabriel e Helder - Engenharia de Computação"),

    html.Div(style={"display": "flex"}, children=[
        # Left panel with controls
        html.Div([
            html.H2("Busca de rotas:", id="busca-title"),

            html.Label("Origem"),
            dcc.Dropdown(
                id="origin",
                options=station_options,
                placeholder="Selecione a estação de origem",
                style={"marginBottom": "10px", "width": "100%"}
            ),

            html.Label("Destino"),
            dcc.Dropdown(
                id="destination",
                options=station_options,
                placeholder="Selecione a estação de destino",
                style={"width": "100%"}
            ),

            html.Div(style={"marginTop": "20px"}, children=[
                html.Button("Calcular rota", id="botao-calcular", n_clicks=0)
            ]),

            html.Div(id="info-rota"),
            html.Div(id="saida-proximo-trem"),
        ], id="left-section"),

        # Right panel with route map
        html.Div([
            dcc.Graph(id="mapa-rota")
        ], id="right-section")
    ]),
    html.Footer("Pontifícia Universidade Católica de Minas Gerais - 2025")
])

@app.callback(
    [Output("mapa-rota", "figure"),
     Output("info-rota", "children"),
     Output("saida-proximo-trem", "children")],
    [Input("botao-calcular", "n_clicks")],
    [State("origin", "value"),
     State("destination", "value")]
)
def update_mapa(n_clicks, orig_id, dest_id):
    """
    Updates the map and route information based on the selected origin and destination.

    Args:
        n_clicks (int): Number of times the calculate button has been clicked
        orig_id (int): ID of the origin station
        dest_id (int): ID of the destination station

    Returns:
        tuple: 
            - Figure with the plotted route on the map
            - Route information text
            - Next train arrival time at destination
    """
    AVERAGE_SPEED = 30.0  # Average speed in km/h

    if not n_clicks or orig_id is None or dest_id is None or orig_id == dest_id:
        return go.Figure(), "", ""

    orig = next(v for v in vertices if v.id == orig_id)
    dest = next(v for v in vertices if v.id == dest_id)
    path = get_short_path(vertices, predecessors, orig, dest)

    if not path:
        return go.Figure(), "Nenhuma rota encontrada.", ""

    # Calculate total travel distance
    total_distance = 0.0
    for i in range(len(path) - 1):
        o = path[i].id - 1
        d = path[i + 1].id - 1
        total_distance += length_matrix[o][d]

    print(total_distance)

    # Calculate travel time in minutes and hours
    total_minutes = total_distance / AVERAGE_SPEED * 60.0
    total_hours = total_minutes / 60.0

    hora_formatada = somar_horas_decimais(total_hours)

    minutos = int(total_minutes)
    segundos = int((total_minutes - minutos) * 60)
    minuto_formatado = f"{minutos:02d}:{segundos:02d}"

    # Map data
    lats = [v.lat for v in path]
    lons = [v.lon for v in path]
    names = [f"{v.station_name} ({v.line})" for v in path]

    fig = go.Figure(go.Scattermapbox(
        mode="markers+lines",
        lat=lats,
        lon=lons,
        marker={'size': 10, 'color': "#00AD54"},
        text=names,
        line=dict(width=3, color='blue')
    ))

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=12,
        mapbox_center={"lat": float(path[0].lat), "lon": float(path[0].lon)},
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    # Informational text
    info_text = f"Rota de {orig.station_name} até {dest.station_name} com {len(path)-1} conexões. Distância total de {round(total_distance,2)} km."
    proximo_trem_text = f"Chegada prevista à {dest.station_name} às {hora_formatada} (duração: {(minuto_formatado)} minutos)."

    return fig, info_text, proximo_trem_text

if __name__ == "__main__":
    """
    Application entry point. If required Floyd-Warshall data files do not exist, they are generated.
    Then, the Dash server is started in debug mode.
    """
    if not (os.path.exists("files/predecessors.txt") and os.path.exists("files/floyd_washal_lenght.txt")):
        generate_floyd_warshall()

    app.run(debug=True)
