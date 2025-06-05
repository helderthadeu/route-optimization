import json
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from os import path

subway_lines = [ 
{"lat":40.706476001106005, "long":-74.01105599991755},
{"lat":40.71002266658424, "long":-74.00793800110387},
{"lat":40.71323378962671, "long":-74.00340673031336},
{"lat":40.71817387697391, "long":-73.99982638545937},
{"lat":40.720246883147254, "long":-73.99380690654237},
{"lat":40.71830605618619, "long":-73.98740940202974},
{"lat":40.708383000017925, "long":-73.95783200075729},
{"lat":40.706889998054, "long":-73.95348800038457},
{"lat":40.703844000042096, "long":-73.94735499884204},
{"lat":40.70040440298112, "long":-73.94137734838365},
{"lat":40.6971950005145, "long":-73.9356230012996},
{"lat":40.69317200129202, "long":-73.92850899927413},
{"lat":40.689583999013905, "long":-73.92215600150752},
{"lat":40.686415270704344, "long":-73.9166388842194},
{"lat":40.68285130087804, "long":-73.91038357033376},
{"lat":40.676998000003756, "long":-73.89852600159652},
{"lat":40.67802821447783, "long":-73.89165772702445},
{"lat":40.679777998961164, "long":-73.8851940021643},
{"lat":40.68152000045683, "long":-73.87962599910783},
{"lat":40.68315265707736, "long":-73.87392925215778},
{"lat":40.689616000838754, "long":-73.87332199882995},
{"lat":40.691290001246735, "long":-73.86728799944963},
{"lat":40.69242699966103, "long":-73.86008700006875},
{"lat":40.69370399880105, "long":-73.85205199740794},
{"lat":40.69516599823373, "long":-73.84443500029684},
{"lat":40.697114810696476, "long":-73.83679338454697},
{"lat":40.700481998515315, "long":-73.82834900017954},
{"lat":40.700382424235, "long":-73.80800471963833},
{"lat":40.70206737621188, "long":-73.80109632298924}]


class vertice:
    def __init__(self, id:int, lat:float, lon:float, station_name:str, line:str, complex_id:int):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.station_name = station_name
        self.line = line
        self.complex_id = complex_id
    
    # def add_line(self, line):
    #     if line not in self.lines:
    #         self.lines.append(line)
        
    def print(self):
        print(f"Coordinates: {self.lat}, {self.lon} - Line: {self.line} ID: {self.id} Name: {self.station_name} Complex ID: {self.complex_id}")
    def to_string(self):
        return f"Coordinates: {self.lat}, {self.lon} - Line: {self.line} ID: {self.id} Name: {self.station_name} Complex ID: {self.complex_id}"
            
def get_short_path(vertices: list[vertice], predecessors: list[list[vertice]], origin: vertice, destiny: vertice)-> list[vertice]:
    path = []
    try:
        i = next(idx for idx, v in enumerate(vertices) if v.id == origin.id)
        j = next(idx for idx, v in enumerate(vertices) if v.id == destiny.id)
    except StopIteration:
        print("Erro: origem ou destino não está na lista de vértices.")
        return []

    if predecessors[i][j] is None and origin.id != destiny.id:
        print("Nenhum caminho entre os vértices.")
        return []

    current = destiny
    while current.id != origin.id:
        
        path.insert(0, current)
        current_idx = next(idx for idx, v in enumerate(vertices) if v.id == current.id)
        pred = predecessors[i][current_idx]
        if pred is None:
            print("Caminho incompleto — predecessor ausente.")
            return []
        current = pred
        if len(path) > len(vertices):
            print("Possível ciclo no caminho.")
            return []
    path.insert(0, origin)
    return path


if path.isfile("files\\predecessors.txt") and path.isfile("files\\floyd_washal_lenght.txt"):
    predecessors = []
    vertices = []
    lengh_matrix = []
with open("files\\predecessors.txt", "r") as file:
    for index, line in enumerate(file):
        values = line.split("@")
        predecessors.append([])
        
        for v in values:
            if v == "None":
                predecessors[index].append(None)
            elif v.split(";")[0].isnumeric():
                
                temp = v.split(";")
                # print(temp[0])
                values = vertice(temp[0], temp[1], temp[2],temp[3],line=temp[4], complex_id=temp[5])
                predecessors[index].append(values)
with open("files\\vertices.txt", "r") as file:
    for index, line in enumerate(file):
        values = line.strip().split("@")
        print(values[13])
        for v in values:    
            if v.split(";")[0].isnumeric():
                temp = v.split(";")
                # print(temp[0])
                values = vertice(temp[0], temp[1], temp[2],temp[3],line=temp[4], complex_id= temp[5])
                vertices.append(values)
with open("files\\floyd_washal_lenght.txt", 'r') as file:
    for line in file:
        # Remove espaços em branco no início/fim e quebra de linha
        line = line.strip()
        
        # Converte os valores para float e ignora strings vazias
        row = [float(x) for x in line.split() if x]
        
        if row:  # Só adiciona se a linha não estiver vazia
            lengh_matrix.append(row)

# get_short_path(vertices, predecessors, vertices[0],vertices[1])
temp = []
print(vertices[12].to_string())
print(vertices[78].to_string())
print(f"Short lenght from 13 to 79: {lengh_matrix[15][32]}")
short_path = (get_short_path(vertices, predecessors, vertices[15],vertices[32]))
# print(short_path)
# Extrair coordenadas
# for element in file["elements"]:
#     for node in element["geometry"]:
#         lats.append(node["lat"])
#         lons.append(node["lon"])
            

lats, lons = [], []
for element in short_path:
        lats.append(float(element.lat))
        lons.append(float(element.lon))

center_lat = sum(lats) / len(lats)
center_lon = sum(lons) / len(lons)


# Criar o mapa (Scattermap corrigido)
fig = go.Figure(go.Scattermap(
    mode="markers+lines",  # Corrigido: "markers" (não "markers")
    lon=lons,
    lat=lats,
    marker={'size': 5},
    showlegend=False  # Opcional: remove a legenda
))


# Configurar layout do mapa (tudo em uma única chamada)
fig.update_layout(
    mapbox=dict(
        zoom=14,
        style="open-street-map",
        center=dict(lon=center_lon, lat=center_lat),
        uirevision="constant"  # Mantém o estado do zoom/pan durante atualizações,
        
    )
)

# Inicializar o app Dash
app = dash.Dash(__name__)

'''
# Layout do app
app.layout = html.Div([
    html.H1("Mapa Interativo com Dash"),
    html.Div([
        dcc.Input(id="input-text", type="text", placeholder="Digite algo..."),
        html.Button("Clique aqui", id="btn-submit", n_clicks=0)
    ], id= "header"),
    dcc.Graph(id="mapa", figure=fig,style={
        'height': '80vh',  # 80% da altura da tela
        'width': '60%',   # Largura total do container
    }),
    html.Div(id="output-text")
])
'''
app.layout = html.Div([
    html.H1("Mapa Interativo com Dash", className="title"),

    html.Div([
        html.Div([
            html.Label("Origem:"),
            dcc.Input(id="input-origem", type="text", placeholder="Digite a origem...", className="input-box"),

            html.Label("Destino:"),
            dcc.Input(id="input-destino", type="text", placeholder="Digite o destino...", className="input-box"),
            html.Button("Buscar", id="btn-destino", n_clicks=0, className="btn"),

            html.Div(id="output-1", className="output-box"),
            html.Div(id="output-2", className="output-box"),
            html.Div(id="output-3", className="output-box")
        ], className="left-panel"),

        html.Div([
            dcc.Graph(id="mapa", figure=fig, className="mapa")
        ], className="right-panel")
    ], className="content")
    
])


'''
# Callback para interação
@app.callback(
    Output("output-text", "children"),
    Input("btn-submit", "n_clicks"),
    Input("input-text", "value")
)
'''

def update_output(n_clicks, input_text):
    return f"Botão clicado {n_clicks} vezes. Texto: {input_text}"

if __name__ == "__main__":
    app.run(debug=True, port=8051)
    # for index, l in enumerate(lats[1:]):
    #     print("another added")
    #     fig.add_trace(
    #         mode = "markers+lines",
    #         lon = l,
    #         lat = lons[index],
    #         marker = {'size': 5}
    #     )
    