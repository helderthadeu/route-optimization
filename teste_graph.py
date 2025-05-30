import networkx as nx
import math
import chardet
import numpy
import json

num_of_lines = 10


def floyd_warshall(graph, vertices):
    subgraphs = graph
    predecessor = []
    for index_i, i in enumerate(graph):
        predecessor.append([])
        for index_j, j in enumerate(graph):
            if i == j:
                subgraphs[index_i][index_j] = 0
                predecessor[index_i].append(0)
            elif subgraphs[index_i][index_j] == 0:
                predecessor[index_i].append(0)
                subgraphs[index_i][index_j] = numpy.inf
            else:
                predecessor[index_i].append(vertices[index_j])
                
    # for index_i, i in enumerate(predecessor):
    #     print(f"{i}")
        
                
    for l in subgraphs:
        for index_k, k in enumerate(subgraphs):
            for index_i, i in enumerate(subgraphs):
                for index_j, j in enumerate(subgraphs):
                    if subgraphs[index_i][index_j] > subgraphs[index_i][index_k] + subgraphs[index_k][index_j]:
                        subgraphs[index_i][index_j] = subgraphs[index_i][index_k] + subgraphs[index_k][index_j]
                        predecessor[index_i][index_j] = vertices[index_k]
            # print(subgraphs)
    return [subgraphs, predecessor]
    
def define_vertice(data):
    vertices = []
    for i in data[1:]:
        for index, j in enumerate(i):
            if (index == 4 or index == 8) and j not in vertices:
                vertices.append(j)
    return vertices

def load_data(file_path):
    """Load JSON data from a file with automatic encoding detection.
    
    Args:
        file_path (str): Path to the JSON file to load.
        
    Returns:
        dict: The parsed JSON data, or None if an error occurs.
    """
    try:
        # Detect file encoding
        with open(file_path, 'rb') as file:
            encoding = chardet.detect(file.read())['encoding']
        
        # Load JSON data with detected encoding
        with open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
            
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} contains invalid JSON.")
    except Exception as e:
        print(f"Unexpected error loading {file_path}: {str(e)}")
    
    return None

def get_routes(json_data):
    """Extract route information from JSON data.
    
    Args:
        json_data (dict): The loaded JSON data containing route elements.
        
    Returns:
        list: A list of dictionaries with route information.
    """
    
    
    
    if not json_data or 'elements' not in json_data:
        print("Error: Invalid or empty JSON data.")
        return []
    
    routes = []
    for element in json_data["elements"]:
        if 'nodes' not in element or 'geometry' not in element:
            continue
            
        nodes = element["nodes"]
        geometry = element["geometry"]
        
        # Add segments between all consecutive nodes
        for i in range(len(nodes)-1):
            route_info = {
                "id": element["id"],
                "init": nodes[i],
                "end": nodes[i+1],
                "start_lat": geometry[i]["lat"],
                "start_lon": geometry[i]["lon"],
                "end_lat": geometry[i+1]["lat"],
                "end_lon": geometry[i+1]["lon"]
            }
            
            routes.append(route_info)

    
    return routes

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

def get_lib_graph(routes):
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
        G.add_node(route["init"])
        G.add_node(route["end"])
        distance = calc_distance(
            route["start_lat"],route["start_lon"],
            route["end_lat"],route["end_lon"]
        )
        G.add_edge(route["init"], route["end"], weight=distance)
    
    # Print graph information
    print("Graph nodes:", G.nodes())
    print(f"Vertices: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    
    # Example path calculation
    try:
        print("Example path:",  nx.floyd_warshall(G, 62994618))
        print("Example lenght:", nx.dijkstra_path_length(G, 62994618, 61851591))
        
    except nx.NodeNotFound as e:
        print(f"Path calculation error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in path calculation: {str(e)}")

if __name__ == "__main__":
    # Load the data from the file
    json_data = load_data("files\\PadreEustaquio.json")
    
    if json_data:
        routes = get_routes(json_data)
        if routes:
            get_lib_graph(routes)
    
if __name__=="__main__":
    # Load the data from the file
    json_ = load_data("files\\PadreEustaquio.json")
    
    routes = get_routes(json_)
    get_lib_graph(routes)
    
    # for element in file["elements"]:
#     for node in element["geometry"]:
#         lats.append(node["lat"])
#         lons.append(node["lon"])
