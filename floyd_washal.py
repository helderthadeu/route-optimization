import chardet
import numpy

num_of_lines = 10

def load_data(file_path):
    raw = []
    data = []
    print("Loading data...")
    try:
        with open(file_path, 'rb') as file:
            result = chardet.detect(file.read())

        with open(file_path, 'r', encoding=result['encoding']) as file:
            raw = [next(file) for _ in range(num_of_lines)]     

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []
    
    
    for line in raw:
        # Split the line into a list of values
        values = line.split(';')
        # Append the list of values to the data list
        data.append(values)
    
    return data

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

if __name__=="__main__":
    # Load the data from the file
    data = load_data("data.csv")
    vertices =  define_vertice(data)
    # Print the loaded data
    
    # for vertice in vertices:
    graph = get_graph(vertices, data)
    print(vertices)
    with open("output.txt", "w") as file:
        # for index, line in enumerate(graph):
        for row in graph:
            for element in row:
                # print(f"{vertices[index]} | {element}")
                file.write(f"{element}\t|")
            file.write(f"\n")
        
        file.write(f"\n\n\n\n")
        floyd_warshall_result = floyd_warshall(graph, vertices)
        minimum = floyd_warshall_result[0]
        predecessors = floyd_warshall_result[1]
        for index, row in enumerate(minimum):
            print(f"{vertices[index]} | {row}")
            for element in row:
                file.write(f"{element} | ")
            file.write(f"\n")
            
        
        file.write(f"\n\n\n\n")
        print("\n\n")
        print(vertices)
        for index, row in enumerate(predecessors):
            print(f"{vertices[index]} | {row}")
            for element in row:
                file.write(f"{element} | ")
            file.write(f"\n")
            
    
