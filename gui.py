import json
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

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

# Carregar dados do arquivo JSON
with open("files/PadreEustaquio.json", "r", encoding="utf-8") as f:
    file = json.load(f)

# Extrair coordenadas
lats, lons = [], []
# for element in file["elements"]:
#     for node in element["geometry"]:
#         lats.append(node["lat"])
#         lons.append(node["lon"])
for element in subway_lines:
        lats.append(element["lat"])
        lons.append(element["long"])

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

# Layout do app
app.layout = html.Div([
    html.H1("Mapa Interativo com Dash"),
    dcc.Input(id="input-text", type="text", placeholder="Digite algo..."),
    html.Button("Clique aqui", id="btn-submit", n_clicks=0),
    dcc.Graph(id="mapa", figure=fig,style={
        'height': '80vh',  # 80% da altura da tela
        'width': '100%',   # Largura total do container
    }),
    html.Div(id="output-text")
])

# Callback para interação
@app.callback(
    Output("output-text", "children"),
    Input("btn-submit", "n_clicks"),
    Input("input-text", "value")
)
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
    