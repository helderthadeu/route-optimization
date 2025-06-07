from os import path
from vertice_definition import vertice
from geopy.distance import geodesic
import math
from file_operate import *
from .manage_files import *
from typing import List

AVERAGE_SPEED = 30
SUBWAY_TICKET = 2.9

def to_string(self):
    return f"Coordinates: {self.lat}, {self.lon} - Line: {self.line} ID: {self.id} Name: {self.station_name} Complex ID: {self.complex_id}"
    
def define_vertice(data: list, id_start: int) -> list[vertice]:
    """
    Create a list of unique vertice objects from the provided data, avoiding duplicates by coordinates.
    Args:
        data (list): List of lists containing station data.
        id_start (int): Initial ID to assign to the first vertice.
    Returns:
        list[vertice]: List of unique vertice objects.
    """
    
    new_vertices: List[vertice] = []
    current_id = id_start
    
    
    for element in data[1:]:
        lat, lon = float(element[0]), float(element[1])
        station_name = str(element[3])
        line = str(element[4])
    
        complex_id = int(element[6])

        exists = False
        for v in new_vertices:
            
            if v.station_name == station_name and v.line == line and v.complex_id == complex_id:
                exists = True
                break
        if exists:
            continue
        else:
            new_vertices.append(vertice(id=current_id, lat=lat, lon=lon, station_name=station_name,line=line, complex_id=complex_id))
            current_id += 1

    return new_vertices

def define_routes(vertices:list[vertice]) -> list[tuple[vertice,vertice]]:
    """
    Define the routes (edges) between vertices based on subway line and complex_id.
    Args:
        vertices (list[vertice]): List of vertice objects.
    Returns:
        list[list[vertice, vertice]]: List of routes as pairs of vertice objects.
    """
    routes = []
    lines = []
    for element in vertices:
        if not element.line in lines:
            lines.append(element.line)
    
    for line in lines:
        previous_vertice = None
        for index, vertice in enumerate(vertices):
            if vertice.line == line:
                if previous_vertice is not None:
                    routes.append((previous_vertice, vertice))
                    routes.append((vertice, previous_vertice))

                previous_vertice = vertice
                            

    for index, vertice in enumerate(vertices[:-1]):
        for vertice2 in vertices[index+1:]:
            if vertice.complex_id == vertice2.complex_id:
                routes.append((vertice, vertice2))
                routes.append((vertice2, vertice))

    return routes

def get_graph(routes:list[tuple[vertice, vertice]], vertices:list[vertice]) -> dict[vertice:list[tuple[vertice, float]]]:
    """
    Build the graph as a dictionary mapping each vertice to its neighbors and the distance to them.
    Args:
        routes (list[list[vertice, vertice]]): List of routes as vertice pairs.
        vertices (list[vertice]): List of vertice objects.
    Returns:
        dict[vertice, list[list[vertice, float]]]: Graph dictionary.
    """
    print("Getting graph...")
    graph = {}
    for vertice in vertices:
        graph[vertice] = []   
    for route in routes:
        dis1_0 = geodesic((route[0].lat, route[0].lon), (route[1].lat, route[1].lon)).kilometers
        dis0_1 = geodesic((route[1].lat, route[1].lon), (route[0].lat, route[0].lon)).kilometers
        if not [route[1], dis1_0] in graph[route[0]]:
            graph[route[0]].append((route[1], dis1_0, None))
        if not [route[0], dis0_1] in graph[route[1]]:
            graph[route[1]].append((route[0], dis0_1, None))
    for v in vertices: 
        for w in vertices:
            disv_w = geodesic((v.lat, v.lon), (w.lat, w.lon)).meters
            if v != w and v.complex_id != w.complex_id and v.line != w.line and disv_w <= 100:
                if [w, disv_w, f"{v.id}|{w.id}"] not in graph[v]:
                    graph[v].append((w, disv_w, f"{v.id}|{w.id}"))
                if [v, disv_w, f"{w.id}|{v.id}"] not in graph[w]:
                    graph[w].append((v, disv_w, f"{w.id}|{v.id}"))

    
    return graph

def calc_distance(lat_initial:float, long_initial:float, lat_final:float, long_final:float) -> float:
    """
    Calculate the distance between two geographic points using the Haversine formula.
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

def floyd_warshall_by_distance(graph:dict[vertice:list[vertice]], vertices:list[vertice]) -> list[list[float]]:
    """
    Compute shortest paths and predecessors for all pairs of vertices using the Floyd-Warshall algorithm.
    Args:
        graph (dict[vertice, list[list[vertice, float]]]): The graph dictionary.
        vertices (list[vertice]): List of vertice objects.
    Returns:
        list: A pair [distance_matrix, predecessor_matrix].
    """
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
            dis = geodesic((i.lat, i.lon), (j.lat, j.lon)).kilometers
            
            ids = []
            for elements_i in  graph[i]:
                ids.append(elements_i[0].id)
            if i in graph.keys() and j.id in ids:
                if i.complex_id == j.complex_id:
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
                    subgraphs[index_j][index_i] = subgraphs[index_i][index_j]
                    predecessor[index_i][index_j] = predecessor[index_k][index_j] 
                    predecessor[index_j][index_i] = predecessor[index_k][index_i]
    return [subgraphs, predecessor]

def calc_factor(wheight_a:float, distance:float, wheight_b:float, crimes:int, riders:int) -> float:
    """
    Calculate a factor based on distance, crimes, and riders.
    Args:
        wheight_a (float): Weight for the distance factor.
        distance (float): Distance between two points.
        wheight_b (float): Weight for the crimes and riders factor.
        crimes (int): Number of crimes at the station.
        riders (int): Number of riders at the station.
    Returns:
        float: Calculated factor.
    """
    
    crimes_per_rider = crimes / riders if riders > 0 else 0
    
    if distance == 0:
        return 0
    return (wheight_a * distance) + (wheight_b * crimes_per_rider)
    
def floyd_warshall_by_factor(graph:dict[vertice:list[vertice]], vertices:list[vertice]) -> list[list[float]]:
    """
    Compute shortest paths and predecessors for all pairs of vertices using the Floyd-Warshall algorithm.
    Args:
        graph (dict[vertice, list[list[vertice, float]]]): The graph dictionary.
        vertices (list[vertice]): List of vertice objects.
    Returns:
        list: A pair [distance_matrix, predecessor_matrix].
    """
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
            
            ids = []
            dis = geodesic((i.lat, i.lon), (j.lat, j.lon)).kilometers
            
            for elements_i in  graph[i]:
                ids.append(elements_i[0].id)
            if i in graph.keys() and j.id in ids:
                if i.complex_id == j.complex_id:
                    dis = 0
                    
                factor = calc_factor(2, dis, 1, i.total_crimes, i.total_riders)
                subgraphs[index_i][index_j] = factor
                subgraphs[index_j][index_i] = factor
                predecessor[index_i][index_j] = i
                predecessor[index_j][index_i] = j

    size = len(subgraphs)
    for index_k in range(size):
        for index_i in range(size):
            for index_j in range(size):                
                if subgraphs[index_i][index_j] > subgraphs[index_i][index_k] + subgraphs[index_k][index_j]:
                    subgraphs[index_i][index_j] = subgraphs[index_i][index_k] + subgraphs[index_k][index_j]
                    subgraphs[index_j][index_i] = subgraphs[index_i][index_j]
                    predecessor[index_i][index_j] = predecessor[index_k][index_j] 
                    predecessor[index_j][index_i] = predecessor[index_k][index_i]
    return [subgraphs, predecessor]

def load_graph_from_file(filepath:str) -> dict[vertice:list[list[vertice, float]]]:
    """
    Load a graph from a file in the custom format used by this project.
    Args:
        filepath (str): Path to the file containing the graph data.
    Returns:
        dict: The loaded graph as a dictionary.
    """
    graph = {}
    with open(filepath, "r") as file:
        for line in file:
            parts = line.strip().split("@")
            if not parts[0]:
                continue
            v_data = parts[0].split(";")
            v = vertice(int(v_data[0]), float(v_data[1]), float(v_data[2]), v_data[3], v_data[4], int(v_data[5]))
            graph[v] = []
            for edge in parts[1:]:
                if edge and len(edge.split(";")) >= 7:
                    e_data = edge.split(";")
                    v2 = vertice(int(e_data[0]), float(e_data[1]), float(e_data[2]), e_data[3], e_data[4], int(e_data[5]))
                    weight = float(e_data[6])
                    graph[v].append([v2, weight])
    return graph

def get_short_path(vertices: list[vertice], predecessors: list[list[vertice]], origin:vertice, destiny:vertice) -> list[vertice]:
    """
    Retrieve the shortest path between two vertices using the predecessor matrix.
    Args:
        vertices (list[vertice]): List of vertice objects.
        predecessors (list[list[vertice]]): Predecessor matrix from Floyd-Warshall.
        origin (vertice): Starting vertice.
        destiny (vertice): Destination vertice.
    Returns:
        list[vertice]: List of vertices representing the shortest path, or empty if not found.
    """
    path = []
    try:
        i = vertices.index(origin)
        j = vertices.index(destiny)
    except StopIteration:
        print("Erro: origin and destiny outside from the list.")
        return []

    if predecessors[i][j] is None:
        if int(origin.id) == int(destiny.id):
            return [origin]
        print("Any path founded.")
        return []

    current = destiny
    path_length = 0
    max_path_length = len(vertices)  
    
    while int(current.id) != int(origin.id) and path_length <= max_path_length:
        path.insert(0, current)
        current_idx = vertices.index(current)
        pred = predecessors[i][current_idx]
        
        if pred is None:
            print("Incomplete path.")
            return []
            
        current = pred
        path_length += 1

    if path_length > max_path_length:
        print("Possibility of cicle.")
        return []

    path.insert(0, origin)
    return path

def generate_floyd_warshall():
    """
    Generate the Floyd-Warshall matrices and save them to files for later use.
    Reads station data, builds the graph, computes shortest paths, and saves results.
    """
    file_path = path.join("src","subway_files", "all_stations_results.csv")
    
    id_counter = 1
    vertices = []
    routes = []
    data = load_data_csv(file_path)
    # print(data)
    vertices = define_vertice(data, id_counter)
    routes = define_routes(vertices)
        
    id_counter = len(vertices)

    graph = get_graph(routes, vertices)
    floyd_warshall_result, predecessors = floyd_warshall_by_distance(graph, vertices) 
    
    save_graph_to_file(graph, "src\\files\\graph.txt")
    save_fload_warshall_to_file(floyd_warshall_result, "src\\files\\floyd_washal_lenght.txt")
    save_predecessors_to_file(predecessors, "src\\files\\predecessors.txt")
    save_vertices_to_file(vertices, "src\\files\\vertices.txt")
