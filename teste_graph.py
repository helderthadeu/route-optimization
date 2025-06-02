import networkx as nx
import math
import chardet
import numpy
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

def get_lib_graph(routes:list[list[vertice, vertice]]):
    """Create a graph from route data using NetworkX.
    
    Args:
        routes (list): List of route segments as returned by get_routes().
    """
    if not routes:
        print("Error: No routes provided to create graph.")
        return
    
    G = nx.Graph()
    
    # Add all nodes and edges
    for route in routes:
        G.add_node(route[0].id)
        G.add_node(route[1].id)
        distance = calc_distance(
            route[0].lat,route[0].lon,
            route[1].lat,route[1].lon
        )
        G.add_edge(route[0].id, route[1].id, weight=distance)
    
    # Print graph information
    # print("Graph nodes:", G.nodes())
    print(f"Vertices: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    
    # Example path calculation
    try:
        # print("Example path:",  nx.floyd_warshall(G)),
        print("Getting Floyd-Warshall graph...")
        predecessors, distance = nx.floyd_warshall_predecessor_and_distance(G)

        # Reconstruir o caminho entre 13 e 79
        path = nx.reconstruct_path(13, 79, predecessors)
        for i in path:
            print(f"{i}")

        # for i in distance[1][0]:
        # print(f"Menor distância: {distance[1][0]}")
        with open("files\\teste.txt", "w") as file:
            for i in distance:
                for j in distance[i]:
                    file.write(f"{distance[i][j]} ")
                file.write("\n")
            
                
        # print("Example lenght:", nx.dijkstra_path_length(G, 62994618, 61851591))
        
    except nx.NodeNotFound as e:
        print(f"Path calculation error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in path calculation: {str(e)}")

if __name__ == "__main__":
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
    
    get_lib_graph(routes)
