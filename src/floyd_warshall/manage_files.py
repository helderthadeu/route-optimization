from src.models.vertice_definition import vertice
from src.models.graph_definition import graph


def save_graph_to_file(graph: graph, filepath:str):
    """
    Save the graph to a file in a custom text format.
    Each line represents a vertice and its edges, separated by '@'.
    Args:
        graph (dict): The graph dictionary with vertice keys and edge lists.
        filepath (str): Path to the output file.
    """
    adjacency = graph.adjacency_list
    with open(filepath, "w") as file:
        for key in adjacency.keys():
            temp = adjacency[key]
            file.write(f"{key.id};{key.lat};{key.lon};{key.station_name};{key.line};{key.complex_id};{key.crime_rate}@")
            for v in temp:
                file.write(f"{v[0].id};{v[0].lat};{v[0].lon};{v[0].station_name};{v[0].line};{v[0].complex_id};{key.crime_rate};{v[1]};{v[2]}@")
            file.write("\n")      

def save_fload_warshall_to_file(floyd_warshall_result:list[list[float]], filepath:str):
    """
    Save the Floyd-Warshall result matrix to a file.
    Each row is written as a line of space-separated values.
    Args:
        floyd_warshall_result (list): The result matrix from Floyd-Warshall.
        filepath (str): Path to the output file.
    """
    with open(filepath, "w") as file:
        for i in floyd_warshall_result:
            for j in i:
                file.write(f"{j} ")
            file.write("\n")

def save_predecessors_to_file(predecessors:list[list[vertice]], filepath:str):
    """
    Save the predecessors matrix to a file in a custom format.
    Each predecessor is written as a string or 'None', separated by '@'.
    Args:
        predecessors (list): The predecessor matrix from Floyd-Warshall.
        filepath (str): Path to the output file.
    """
    with open(filepath, "w") as file:
        for i in predecessors:
            for j in i:
                if j is None:
                    file.write(f"{j}@")
                else:
                    file.write(f"{j.id};{j.lat};{j.lon};{j.station_name};{j.line};{j.complex_id};{j.crime_rate}@")
            file.write("\n")

def save_vertices_to_file(vertices:list[vertice], filepath:str):
    """
    Save the list of vertices to a file in a custom format.
    Each vertice is written as a string, separated by '@'.
    Args:
        vertices (list): List of vertice objects.
        filepath (str): Path to the output file.
    """
    with open(filepath, "w") as file:
        for i in vertices:
            file.write(f"{i.id};{i.lat};{i.lon};{i.station_name};{i.line};{i.complex_id};{i.crime_rate}@")

def load_graph_from_file(filepath:str) -> graph:
    """
    Load a graph from a file in the custom format used by this project.
    Args:
        filepath (str): Path to the file containing the graph data.
    Returns:
        dict: The loaded graph as a dictionary.
    """
    adjacency = {}
    with open(filepath, "r") as file:
        for line in file:
            parts = line.strip().split("@")
            if not parts[0]:
                continue
            # Carrega o vértice principal
            v_data = parts[0].split(";")
            v = vertice(int(v_data[0]), float(v_data[1]), float(v_data[2]), v_data[3], v_data[4], int(v_data[5]),float(v_data[6]))
            adjacency[v] = []
            # Carrega as arestas
            for edge in parts[1:]:
                if edge and len(edge.split(";")) >= 7:
                    e_data = edge.split(";")
                    v2 = vertice(int(e_data[0]), float(e_data[1]), float(e_data[2]), e_data[3], e_data[4], int(e_data[5]),float(v_data[6]))
                    weight = float(e_data[6])
                    adjacency[v].append([v2, weight,None if e_data[7] == "None" else str(e_data[7])])
    
    return graph(adjacency_list=adjacency)

def load_predecessors_from_file(filepath:str) -> list[list[vertice]]:
    """
    Load the predecessors matrix from a file in the custom format.
    Args:
        filepath (str): Path to the file containing the predecessors data.
    Returns:
        list: The loaded predecessor matrix.
    """
    predecessors = []
    with open(filepath, "r") as file:
            for index, line in enumerate(file):
                values = line.split("@")
                predecessors.append([])
                
                for v in values:
                    if v == "None":
                        predecessors[index].append(None)
                    elif v.split(";")[0].isnumeric():
                        
                        temp = v.split(";")
                        # print(temp[0])
                        values = vertice(temp[0], temp[1], temp[2],temp[3],line=temp[4], complex_id=temp[5], crime_rate=temp[6])
                        predecessors[index].append(values)
    return predecessors

def load_vertices_from_file(filepath:str) -> list[vertice]:
    """
    Load a list of vertices from a file in the custom format.
    Args:
        filepath (str): Path to the file containing the vertices data.
    Returns:
        list: The loaded list of vertice objects.
    """
    vertices = []
    with open(filepath, "r") as file:
        for index, line in enumerate(file):
            values = line.strip().split("@")
            for v in values:    
                if v.split(";")[0].isnumeric():
                    temp = v.split(";")
                    # print(temp[0])
                    values = vertice(temp[0], temp[1], temp[2],temp[3],line=temp[4], complex_id= temp[5], crime_rate= temp[6])
                    vertices.append(values)
    return vertices

def load_length_matrix_from_file(filepath:str) -> list[list[float]]:
    """
    Load the length (distance) matrix from a file.
    Each line is parsed as a list of floats.
    Args:
        filepath (str): Path to the file containing the matrix data.
    Returns:
        list: The loaded matrix as a list of lists of floats.
    """
    lengh_matrix = []
    with open(filepath, 'r') as file:
        for line in file:
            
            line = line.strip()
            
            row = [float(x) for x in line.split() if x]
            
            if row:  
                lengh_matrix.append(row)
    return lengh_matrix
