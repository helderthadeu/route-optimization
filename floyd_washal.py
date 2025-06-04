import chardet
import numpy
import json
from os import path
from glob import glob
from geopy.distance import geodesic
import math

NUM_OF_LINES = 999999
AVERAGE_SPEED = 30
SUBWAY_TICKET = 2.9

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
    
def load_data_csv(file_path):
    raw = []
    data = []
    print("Loading data...")
    try:
        with open(file_path, 'rb') as file:
            result = chardet.detect(file.read())

        with open(file_path, 'r', encoding=result['encoding']) as file:
            for _ in range(NUM_OF_LINES):
                line = file.readline()
                if not line:  # Se chegou ao final do arquivo
                    break
                raw.append(line.replace("\n", ""))
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []
    
    
    for line in raw:
        # Split the line into a list of values
        values = line.split(',')
        # Append the list of values to the data list
        data.append(values)
    
    return data

def load_data_json(file_path):
    json_file = []
    
    print("Loading data...")
    try:
        with open(file_path, 'rb') as file:
            result = chardet.detect(file.read())

        with open(file_path, 'r', encoding=result['encoding']) as file:
            json_file = json.load(file)
    
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []
    
    return json_file
  
def define_vertice(data: list, id_start: int) -> list[vertice]:
    new_vertices = []
    current_id = id_start
    
    
    for element in data[1:]:
        lat, lon = float(element[0]), float(element[1])
        station_name = str(element[3])
        line = str(element[4])
    
        complex_id = int(element[6])
        
        # print(lat)
        # Verifica se o vértice já existe na lista global (vertices)
        found = None
        for v in new_vertices:
            
            if v.lat == lat and v.lon == lon:
                found = v
                break
        if found != None:
            continue
            new_vertices.append(found)
        else:
            
            new_vertices.append(vertice(id=current_id, lat=lat, lon=lon, station_name=station_name,line=line, complex_id=complex_id))
            current_id += 1
    return new_vertices

def define_routes(vertices:list[vertice])->list[list[vertice,vertice]]:
    routes = []
    lines = []
    for element in vertices:
        if not element.line in lines:
            lines.append(element.line)
    
    for line in lines:
        previous_vertice = None
        for index, vertice in enumerate(vertices):
            if vertice.line == line:
                if previous_vertice is None:
                    previous_vertice = vertice
                else:
                    routes.append([previous_vertice, vertice])
                    routes.append([vertice, previous_vertice])
                    previous_vertice = vertice
                    
                
    
    for index,  vertice in enumerate(vertices[:-1]):
        for index2, vertice2 in enumerate(vertices[:-1]):
            if index2 == index:
                continue
            elif vertice.complex_id == vertice2.complex_id:
                if vertice.id != vertice2.id:
                    # print(f"Route: {vertice.to_string()} - {vertice2.to_string()}")
                    routes.append([vertice, vertice2])
            # elif vertices[index2] == vertices[index+1] and :
            

    return routes

def get_graph(routes:list[list[vertice, vertice]], vertices:list[vertice]) -> dict[vertice:list[vertice]]:
    print("Getting graph...")
    graph = {}
    for vertice in vertices:
        graph[vertice] = []   
    for route in routes:
        if not route[1] in graph[route[0]]:
            graph[route[0]].append(route[1])
        if not route[0] in graph[route[1]]:
            graph[route[1]].append(route[0])

    return graph

def calc_distance(lat_initial, long_initial, lat_final, long_final):
    """Calculate the distance between two geographic points using Haversine formula.
    
    Args:
        lat_initial (float): Starting latitude in degrees.
        long_initial (float): Starting longitude in degrees.
        lat_final (float): Ending latitude in degrees.
        long_final (float): Ending longitude in degrees.
        
    Returns:
        float: Distance between the points in meters.
    """
    # Convert degrees to radians
    d2r = math.pi / 180.0
    lat1, lon1 = lat_initial * d2r, long_initial * d2r
    lat2, lon2 = lat_final * d2r, long_final * d2r
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return 6371 * c  # Earth radius in meters

# def get_null_edge(graph:dict[vertice:list[vertice]], vertices:list[vertice]):
# 
#     for node in  graph.keys():
#         connections = graph[node]
#         for vertice in vertices:
#                 if vertice not in connections:
#                     distace = geodesic((node.lat, node.lon), (vertice.lat, vertice.lon)).meters
#                     if distace < 70:
#                         pass
    

def floyd_warshall_by_distance(graph:dict[vertice:list[vertice]], vertices:list[vertice]):
    subgraphs = []
    predecessor = []
    print("Getting Floyd Washal...")

    n = len(vertices)
    subgraphs = [[float('inf')] * n for _ in range(n)]
    predecessor = [[None] * n for _ in range(n)]
    for i in range(n):
        subgraphs[i][i] = 0
        predecessor[i][i] = vertices[i] 
        
    for index_i, i in enumerate(vertices):
        for index_j, j in enumerate(vertices):

            if i in graph.keys() and j in graph[i]:
                # dis_ij = calc_distance(vertices[index_i].lat,vertices[index_i].lon,vertices[index_j].lat, vertices[index_j].lon)
                # dis_ji = calc_distance(vertices[index_j].lat,vertices[index_j].lon,vertices[index_i].lat, vertices[index_i].lon)
                if i.complex_id != j.complex_id:
                    dis = geodesic((i.lat, i.lon), (j.lat, j.lon)).kilometers
                else:
                    dis = 0
                subgraphs[index_i][index_j] = dis
                subgraphs[index_j][index_i] = dis
                predecessor[index_i][index_j] = i
                predecessor[index_j][index_i] = j

    size = len(subgraphs)
    for index_k in range(size):
        for index_i in range(size):
            for index_j in range(size):                

                if subgraphs[index_i][index_j] > subgraphs[index_i][index_k] + subgraphs[index_k][index_j]:
                    subgraphs[index_i][index_j] = subgraphs[index_i][index_k] + subgraphs[index_k][index_j]
                    subgraphs[index_j][index_i] = subgraphs[index_i][index_j]  # Mantém a simetria da distância
                    # print(f"Distance: {subgraphs[index_i][index_j]}")
                    predecessor[index_i][index_j] = predecessor[index_k][index_j]  # Atualiza predecessor
                    predecessor[index_j][index_i] = predecessor[index_k][index_i]
                # print(subgraphs)
    return [subgraphs, predecessor]

def generate_floyd_washal():
    # file_path = path.join("subway_files", "Lines", "*")
    file_path = path.join("subway_files", "all_stations_results.csv")
    
    id_counter = 1
    vertices = []
    routes = []
    # for file in glob(file_path):
    #     data = load_data_csv(file)
    #     vertices_local = define_vertice(data, id_counter, vertices)
    #     for route in define_routes(vertices_local):
    #         routes.append(route)
    #     vertices.extend(v for v in vertices_local if v not in vertices)
    #     id_counter = max(v.id for v in vertices) + 1
    
    data = load_data_csv(file_path)
    # print(data)
    vertices_local = define_vertice(data, id_counter)
    for route in define_routes(vertices_local):
        routes.append(route)
    for v in vertices_local:
        if v not in vertices:
            vertices.append(v)
        
    id_counter = max(v.id for v in vertices) + 1

    graph = get_graph(routes, vertices)
    
    floyd_warshall_result, predecessors = floyd_warshall_by_distance(graph, vertices) 
    with open("files\\graph.txt", "w") as file:
        for key in graph.keys():
            temp = graph[key]
            file.write(f"{key.id};{key.lat};{key.lon};{key.station_name};{key.line};{key.complex_id}@")
            for v in temp:
                file.write(f"{v.id};{v.lat};{v.lon};{v.station_name};{v.line};{v.complex_id}@")
            file.write("\n")
        
    with open("files\\floyd_washal_lenght.txt", "w") as file:
        for i in floyd_warshall_result:
            for j in i:
                file.write(f"{j} ")
            file.write("\n")
    with open("files\\predecessors.txt", "w") as file:
        for i in predecessors:
            for j in i:
                if j is None:
                    file.write(f"{j}@")
                else:
                    file.write(f"{j.id};{j.lat};{j.lon};{j.station_name};{j.line};{j.complex_id}@")
            file.write("\n")
    with open("files\\vertices.txt", "w") as file:
        for i in vertices:
            file.write(f"{i.id};{i.lat};{i.lon};{i.station_name};{i.line};{i.complex_id}@")
        
def get_short_path(vertices: list[vertice], predecessors: list[list[vertice]], origin: vertice, destiny: vertice):
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

if __name__=="__main__":
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
        
        print(f"Short lenght from 13 to 79: {lengh_matrix[12][79]/AVERAGE_SPEED}")
        for index, i in enumerate(get_short_path(vertices, predecessors, vertices[12],vertices[79])):
            print(f"{index+1} - {i.to_string()}")
            
        # print(len(temp))
    else:
        generate_floyd_washal()    
    
