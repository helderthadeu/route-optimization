import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from floyd_utils import load_vertices, load_predecessors, get_short_path  # Suas funções

# Carrega os dados do metrô
vertices = load_vertices("files/vertices.txt")
predecessors = load_predecessors("files/predecessors.txt", vertices)

# Dados GTFS para horários
stops = pd.read_csv("src\\gtfs_files\\stops.txt")
routes = pd.read_csv("src\\gtfs_files\\routes.txt")
trips = pd.read_csv("src\\gtfs_files\\trips.txt")
stop_times = pd.read_csv("src\\gtfs_files\\stop_times.txt")
calendar = pd.read_csv("src\\gtfs_files\\calendar.txt")
day_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

def parse_time(t):
    try:
        h, m, s = map(int, t.split(":"))
        h = h % 24
        return datetime.strptime(f"{h:02}:{m:02}:{s:02}", "%H:%M:%S").time()
    except:
        return None

def sum_time_from_travel(time, minutes_add):
    dummy_date = datetime.combine(datetime.today(), time)
    return (dummy_date + timedelta(minutes=minutes_add)).time()

def next_train_time(line, station, hour, time_travel_minutes):
    today_index = datetime.now().weekday()
    today = day_week[today_index]

    active_services = calendar[calendar[today] == 1]['service_id'].tolist()

    line_prefix = line[0]
    if line_prefix == 'S':
        line_prefix = "SI"
    
    line_id = routes[routes['route_short_name'] == line_prefix]['route_id'].values[0]
    valid_trips = trips[(trips['route_id'] == line_id) & (trips['service_id'].isin(active_services))]

    schedules = stop_times[stop_times['trip_id'].isin(valid_trips['trip_id'])]
    schedules = schedules.merge(stops, on='stop_id')
    station_schedules = schedules[schedules['stop_name'] == station]

    now_plus_time_travel = sum_time_from_travel(hour, time_travel_minutes)
    station_schedules = station_schedules.copy()
    station_schedules['arrival_time_parsed'] = station_schedules['arrival_time'].apply(parse_time)
    next_schedules = station_schedules[station_schedules['arrival_time_parsed'] > now_plus_time_travel]

    if next_schedules.empty:
        return now_plus_time_travel

    next_train = next_schedules.sort_values(by='arrival_time_parsed').iloc[0]
    next_train_hour = next_train['arrival_time_parsed']
    return next_train_hour

# Inicializa app Dash
app = dash.Dash(__name__)

station_options = [{'label': f"{v.station_name} ({v.line})", 'value': v.id} for v in vertices]

app.layout = html.Div([
    html.H1("Busca de Rotas"),
    html.P("Busca de melhores rotas de metrô em Manhattan - Nova York"),
    html.H3("Enzo, Gabriel e Helder - Engenharia de Computação"),
    

    html.Div(style={"display": "flex"}, children=[
        # Div com seletores e botões à esquerda
        html.Div([
            html.H2("Busca de rotas: ", id = "busca-title"),
            html.Label("Origem"),
            dcc.Dropdown(id="origin", options=station_options, placeholder="Selecione a estação de origem", style={"marginBottom": "10px", "width": "100%"}),

            html.Label("Destino"),
            dcc.Dropdown(id="destination", options=station_options, placeholder="Selecione a estação de destino", style={"width": "100%"}),

            html.Div(style={"marginTop": "20px"}, children=[
                html.Button("Calcular rota", id="botao-calcular", n_clicks=0)
            ]),

            html.Div(id="info-rota"),

            html.Div(id="saida-proximo-trem"),
        ],id="left-section"),

        # Div com o mapa à direita
        html.Div([
            dcc.Graph(id="mapa-rota")
        ], id="right-section")
    ])
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
    if not n_clicks or orig_id is None or dest_id is None or orig_id == dest_id:
        return go.Figure(), "", ""

    orig = next(v for v in vertices if v.id == orig_id)
    dest = next(v for v in vertices if v.id == dest_id)

    path = get_short_path(vertices, predecessors, orig, dest)
    if not path:
        return go.Figure(), "Nenhuma rota encontrada.", ""

    time_travel = sum(getattr(path[i], 'weight', 2) for i in range(len(path)-1))

    now = datetime.now().time()
    next_train = next_train_time(orig.line, orig.station_name, now, time_travel)

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
    fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=12,
                      mapbox_center={"lat": float(path[0].lat), "lon": float(path[0].lon)})
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    info_text = f"Rota de {orig.station_name} até {dest.station_name} com {len(path)-1} conexões."
    proximo_trem_text = f"Próximo trem na estação {orig.station_name} às {next_train.strftime('%H:%M:%S')}."

    return fig, info_text, proximo_trem_text

if __name__ == "__main__":
    app.run(debug=True)