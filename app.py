import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

from floyd_utils import load_vertices, load_predecessors, get_short_path  # funções auxiliares

# Importa sua função de cálculo de próximo trem
from src.next_train import next_train_time  # ajuste para seu arquivo real

# Carrega os dados do grafo
vertices = load_vertices("files/vertices.txt")
predecessors = load_predecessors("files/predecessors.txt", vertices)

# Monta opções para dropdown
station_options = [{'label': f"{v.station_name} ({v.line})", 'value': v.id} for v in vertices]

# Inicializa app Dash
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Rota no Metrô (Floyd-Warshall)", style={"textAlign": "center","fontFamily": "Helvetica", "fontSize": "30px","color": "#096309"}),

    html.Div([
        html.Label("Origem", style={"fontWeight": "bold","color": "#096309"}),
        dcc.Dropdown(id="origin", options=station_options, placeholder="Selecione a estação de origem",style={"marginBottom": "20px"}),
        
        html.Label("Destino"),
        dcc.Dropdown(id="destination", options=station_options, placeholder="Selecione a estação de destino"),
    ], style={"width": "50%", "margin": "auto", "fontFamily": "Arial, sans-serif", "fontSize": "18px"}),

    dcc.Graph(id="mapa-rota",style={"marginTop": "30px"}),

    html.Div(id="info-rota", style={
        "whiteSpace": "pre-line",
        "textAlign": "center",
        "marginTop": "20px",
        "fontFamily": "Arial, sans-serif",
        "fontSize": "12px",
        "color": "#096309",  # verde
        "fontWeight": "bold",
        "fontStyle": "italic"
        })
])

@app.callback(
    [Output("mapa-rota", "figure"),
     Output("info-rota", "children")],
    [Input("origin", "value"),
     Input("destination", "value")]
)
def update_mapa(orig_id, dest_id):
    if orig_id is None or dest_id is None or orig_id == dest_id:
        return go.Figure(), ""

    orig = next(v for v in vertices if v.id == orig_id)
    dest = next(v for v in vertices if v.id == dest_id)

    path = get_short_path(vertices, predecessors, orig, dest)
    if not path:
        return go.Figure(), "Nenhuma rota encontrada."

    lats = [p.lat for p in path]
    lons = [p.lon for p in path]
    names = [f"{p.station_name} ({p.line})" for p in path]

    fig = go.Figure(go.Scattermapbox(
        mode="markers+lines",
        lat=lats,
        lon=lons,
        marker={'size': 10, 'color': "red"},
        text=names,
        line=dict(width=3, color='blue')
    ))
    fig.update_layout(
        mapbox_style="open-street-map", 
        mapbox_zoom=12,
        mapbox_center={"lat": float(path[0].lat), "lon": float(path[0].lon)}
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    # Hora atual para usar no cálculo do próximo trem
    now_time = datetime.now().time()

    # Usa sua função para pegar o próximo trem da estação de origem
    try:
        next_train = next_train_time(orig.line, orig.station_name, now_time, 0)
        horario_str = next_train.strftime("%H:%M:%S") if next_train else "Não disponível"
    except Exception as e:
        horario_str = f"Erro ao obter próximo trem: {e}"

    info_text = (
        f"Rota de {orig.station_name} até {dest.station_name} com {len(path)-1} conexões.\n"
        f"Próximo trem saindo de {orig.station_name} em: {horario_str}"
    )

    return fig, info_text

if __name__ == "__main__":
    app.run(debug=True)
