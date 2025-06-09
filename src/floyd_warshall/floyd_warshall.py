from os import path
from src.models.vertice_definition import vertice
from src.models.edge_definition import edge
from src.models.graph_definition import graph
from geopy.distance import geodesic
import math
from src.file_operate import *
from .manage_files import *
from typing import List

AVERAGE_SPEED = 30
SUBWAY_TICKET = 2.9
   
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
        crime_rate_str = element[7].strip()
        crime_rate = float(crime_rate_str) if crime_rate_str != "" else 0.000072

        exists = False
        for v in new_vertices:
            
            if v.station_name == station_name and v.line == line and v.complex_id == complex_id:
                exists = True
                break
        if exists:
            continue
        else:
            new_vertices.append(vertice(id=current_id, lat=lat, lon=lon, station_name=station_name,line=line, complex_id=complex_id, crime_rate=crime_rate))
            current_id += 1

    return new_vertices

def define_routes(vertices:list[vertice]) -> list[edge]:
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
                    routes.append(edge(origin=previous_vertice, destiny=vertice))
                    routes.append(edge(origin=vertice, destiny=previous_vertice))

                previous_vertice = vertice
                            

    for index, vertice in enumerate(vertices[:-1]):
        for vertice2 in vertices[index+1:]:
            if vertice.complex_id == vertice2.complex_id:
                routes.append(edge(origin=vertice, destiny=vertice2))
                routes.append(edge(origin=vertice2, destiny=vertice))

    return routes

def get_graph(routes:list[edge], vertices:list[vertice]) -> graph:
    """
    Build the graph as a dictionary mapping each vertice to its neighbors and the distance to them.
    Args:
        routes (list[list[vertice, vertice]]): List of routes as vertice pairs.
        vertices (list[vertice]): List of vertice objects.
    Returns:
        graph: Graph contains dictionary with adjacency list
    """
    print("Getting graph...")
    adjacency_list = {}
    for vertice in vertices:
        adjacency_list[vertice] = []   
    for route in routes:
        dist_destiny_origin = geodesic((route.origin.lat, route.origin.lon), (route.destiny.lat, route.destiny.lon)).kilometers
        dist_origin_destiny = geodesic((route.destiny.lat, route.destiny.lon), (route.origin.lat, route.origin.lon)).kilometers
        if not [route.destiny, dist_destiny_origin] in adjacency_list[route.origin]:
            adjacency_list[route.origin].append((route.destiny, dist_destiny_origin, None))
        if not [route.origin, dist_origin_destiny] in adjacency_list[route.destiny]:
            adjacency_list[route.destiny].append((route.origin, dist_origin_destiny, None))
    for v in vertices: 
        for w in vertices:
            dist_v_w = geodesic((v.lat, v.lon), (w.lat, w.lon)).meters
            if v != w and v.complex_id != w.complex_id and v.line != w.line and dist_v_w <= 100:
                if [w, dist_v_w, f"{v.id}|{w.id}"] not in adjacency_list[v]:
                    adjacency_list[v].append((w, dist_v_w, f"{v.id}|{w.id}"))
                if [v, dist_v_w, f"{w.id}|{v.id}"] not in adjacency_list[w]:
                    adjacency_list[w].append((v, dist_v_w, f"{w.id}|{v.id}"))
    
    return graph(adjacency_list=adjacency_list)

def floyd_warshall_by_distance(graph:graph, vertices:list[vertice]) -> list[list[float]]:
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
    adjacency = graph.adjacency_list
    subgraphs = [[float('inf')] * n for _ in range(n)]
    predecessor = [[None] * n for _ in range(n)]
    for i in range(n):
        subgraphs[i][i] = 0
        predecessor[i][i] = vertices[i] 
    
    for index_i, i in enumerate(vertices):
        ids = []
        for elements_i in adjacency[i]:
            ids.append(elements_i[0].id)
        for index_j, j in enumerate(vertices):
            if i in adjacency.keys() and j.id in ids:
                dis = geodesic((i.lat, i.lon), (j.lat, j.lon)).kilometers
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
                dist = subgraphs[index_i][index_k] + subgraphs[index_k][index_j]           
                if subgraphs[index_i][index_j] > dist:
                    subgraphs[index_i][index_j] = dist
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
