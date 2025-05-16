import chardet

num_of_lines = 10

def load_data(file_path):
    raw = []
    data = []
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

def floyd_warshall(data):
    # graph = []
    # for i in data:
    #     graph.append([])
    #     for j in i:
    #         if j == i:
    #             graph[i].append(0)
    #         else:
    pass

def define_vertice(data):
    vertices = []
    for i in data[1:]:
        for index, j in enumerate(i):
            if (index == 4 or index == 8) and j not in vertices:
                vertices.append(j)
    return vertices

def get_graph(vertices, data):
    graph = []
    for index_i, i in enumerate(vertices):
        graph.append([])
        for index, j in enumerate(vertices):
            founded = False
            for k in data[1:]:
                if (i == k[4] and j == k[8]) or (i == k[8] and j == k[4]):
                    graph[index_i].append(k[12])
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
    with open("output.txt", "w") as file:
        for index, line in enumerate(get_graph(vertices, data)):
            print(line)
            file.write(f"{line}\n")
        

    
