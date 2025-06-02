import chardet
import numpy
import math
import json
from os import path
from glob import glob

num_of_lines = 999999

class vertice:
    def __init__(self, id:int, lat:float, lon:float):
        self.id = id
        self.lat = lat
        self.lon = lon
    
    def print(self):
        print(f"ID: {self.id} Lat: {self.lat} Lon: {self.lon}")

def load_data_csv(file_path):
    raw = []
    data = []
    print("Loading data...")
    try:
        with open(file_path, 'rb') as file:
            result = chardet.detect(file.read())

        with open(file_path, 'r', encoding=result['encoding']) as file:
            for _ in range(num_of_lines):
                line = file.readline()
                if not line:  # Se chegou ao final do arquivo
                    break
                raw.append(line.strip())
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
  
def define_vertice(data: list, id_start: int, vertices: list[vertice]) -> list[vertice]:
    new_vertices = []
    current_id = id_start
    
    for element in data[1:]:
        lat, lon = float(element[0]), float(element[1])
        # Verifica se o vértice já existe na lista global (vertices)
        found = None
        for v in vertices:
            if v.lat == lat and v.lon == lon:
                found = v
                break
        if found:
            new_vertices.append(found)
        else:
            new_vertices.append(vertice(id=current_id, lat=lat, lon=lon))
            current_id += 1
    return new_vertices

def define_routes(vertices:list) -> list[list[vertice,vertice]]:
    routes = []
    for index,  vertice in enumerate(vertices[:-1]):
        lenght = calc_distance(vertices[index].lat,vertices[index].lon, vertices[index+1].lat,vertices[index+1].lon )
        routes.append([vertices[index], vertices[index+1],lenght])

    return routes

def get_graph(routes:list[list[vertice, vertice]]) -> dict[vertice:list[vertice]]:
    print("Getting graph...")
    graph = {}
    for route in routes:
        if not route[0] in graph.keys():
            graph[route[0]] = [route[1]]
        elif not route[1] in graph[route[0]]:
            graph[route[0]].append(route[1])
        
            
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
    
    return 6371000 * c  # Earth radius in meters

def floyd_warshall(graph:dict[vertice:list[vertice]], vertices:list[vertice]):
    subgraphs = []
    predecessor = []
    print("Getting Floyd Washal...")
    
    v_null = vertice(-1,-1,-1)
    n = len(vertices)
    subgraphs = [[float('inf')] * n for _ in range(n)]
    predecessor = [[None] * n for _ in range(n)]
    for i in range(n):
        subgraphs[i][i] = 0

    for index_i, i in enumerate(vertices):
        for index_j, j in enumerate(vertices):

            if i in graph.keys() and j in graph[i]:
                dis_ij = calc_distance(vertices[index_i].lat,vertices[index_i].lon,vertices[index_j].lat, vertices[index_j].lon)
                dis_ji = calc_distance(vertices[index_j].lat,vertices[index_j].lon,vertices[index_i].lat, vertices[index_i].lon)
                predecessor[index_i][index_j] = j 
                predecessor[index_j][index_i] = i 
                subgraphs[index_i][index_j] = dis_ij 
                subgraphs[index_j][index_i] = dis_ji

    size = len(subgraphs)
    for index_k in range(size):
        for index_i in range(size):
            for index_j in range(size):                
                # print(f"Tamanho: {len(subgraphs[index_i])} | IndexI: {index_i} | IndexJ: {index_j}")
                if subgraphs[index_i][index_j] > subgraphs[index_i][index_k] + subgraphs[index_k][index_j]:
                    subgraphs[index_i][index_j] = subgraphs[index_i][index_k] + subgraphs[index_k][index_j]
                    # print(subgraphs[index_i][index_k] + subgraphs[index_k][index_j])
                    predecessor[index_i][index_j] = vertices[index_k]
            # print(subgraphs)
    return [subgraphs, predecessor]
  
if __name__=="__main__":
    
    file_path = path.join("subway_files", "Lines", "*")
    
    id_counter = 1
    vertices = []
    routes = []
    for file in glob(file_path):
        data = load_data_csv(file)
        vertices_local = define_vertice(data, id_counter, vertices)
        for route in define_routes(vertices_local):
            routes.append(route)
        vertices.extend(v for v in vertices_local if v not in vertices)
        id_counter = max(v.id for v in vertices) + 1
    # for route in routes:
    #     print(f"1- {route[0].id} 2- {route[1].id}")
    # for v in vertices:
    #     v.print()
    graph = get_graph(routes)
    
    # for key, neighbors in graph.items():
    #     print(f"{key.id} -> ", end='')  # imprime o vértice
    # for neighbor in neighbors:
    #     print(neighbor.id, end=' ')  # imprime os vizinhos na mesma linha
    # print()  # quebra de linha depois de cada vértice
    
    floyd_warshall_result, predecessors = floyd_warshall(graph, vertices) 
    # for i in floyd_warshall_result[0]:
    #     print(i)
    # print(floyd_warshall_result)
    # for i in range(5):
    #         for j in  range(5):
    # print(f"Shortest distance: {floyd_warshall_result[1][4]}")
    with open("files\\ofc.txt", "w") as file:
        for i in floyd_warshall_result:
            for j in i:
                file.write(f"{j} ")
        file.write("\n")
    
    # with open("output.txt", "w") as file:
    #     # for index, line in enumerate(graph):
    #     for row in graph:
    #         for element in row:
    #             # print(f"{vertices[index]} | {element}")
    #             file.write(f"{element}\t|")
    #         file.write(f"\n")
        
    #     file.write(f"\n\n\n\n")
    #     floyd_warshall_result = floyd_warshall(graph, vertices)
    #     minimum = floyd_warshall_result[0]
    #     predecessors = floyd_warshall_result[1]
    #     for index, row in enumerate(minimum):
    #         # print(f"{vertices[index]} | {row}")
    #         for element in row:
    #             file.write(f"{element} | ")
    #         file.write(f"\n")
            
        
    #     file.write(f"\n\n\n\n")
    #     # print("\n\n")
    #     # print(vertices)
    #     for index, row in enumerate(predecessors):
    #         # print(f"{vertices[index]} | {row}")
    #         for element in row:
    #             file.write(f"{element} | ")
    #         file.write(f"\n")
            
    
