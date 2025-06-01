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

def define_routes(vertices:list)->list[list[vertice,vertice]]:
    routes = []
    for index,  vertice in enumerate(vertices[:-1]):
        routes.append([vertices[index], vertices[index+1]])

    return routes

def get_graph(vertices, data):
    print("Getting graph...")
    graph = []
    for index_i, i in enumerate(vertices):
        graph.append([])
        for index, j in enumerate(vertices):
            founded = False
            for k in data[1:]:
                if (i == k[4] and j == k[8]) or (i == k[8] and j == k[4]):
                    graph[index_i].append(int(k[12]))
                    founded = True
                    break
            if not founded:
                graph[index_i].append(0)
              
            
    return graph

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
  
if __name__=="__main__":
    
    file_path = path.join("subway_files", "Lines", "*")
    
    id_counter = 1
    vertices = []
    routes = []
    for file in glob(file_path):
        data = load_data_csv(file)
        vertices_local = define_vertice(data, id_counter, vertices)
        for route in define_routes(vertices_local):
            routes.append(route )
        vertices.extend(v for v in vertices_local if v not in vertices)
        id_counter = max(v.id for v in vertices) + 1
    
    
    
    for route in routes:
        print(f"1- {route[0].id} 2- {route[1].id}")
    # for v in vertices:
    #     v.print()
    
    # print(routes[0][0].id)
    # Print the loaded data
    
    # for vertice in vertices:
    # graph = get_graph(vertices, data)
    # # print(vertices)
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
            
    
