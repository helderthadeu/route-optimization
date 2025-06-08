"""
main_cli.py
-------------
Command-line interface for running shortest path queries and graph operations on the subway network.
Loads precomputed Floyd-Warshall matrices and graph data if available, or generates them if not.
Prints the shortest path and step-by-step traversal between two stations.
"""

from os import path
from file_operate import *
from floyd_warshall import *
from next_train import next_train_time, datetime

AVERAGE_SPEED = 30
SUBWAY_TICKET = 2.9

if __name__=="__main__":
    """
    Main entry point for the CLI application.
    Loads graph, vertices, predecessors, and length matrix from files if available.
    Computes and prints the shortest path between two stations, including step-by-step traversal and transfer information.
    If the required files do not exist, generates them using Floyd-Warshall.
    """
    if path.isfile("src\\files\\predecessors.txt") and path.isfile("src\\files\\floyd_washal_lenght.txt"):
        # Load all necessary data from files
        graph = load_graph_from_file("src\\files\\graph.txt")
        predecessors = load_predecessors_from_file("src\\files\\predecessors.txt")
        vertices = load_vertices_from_file("src\\files\\vertices.txt")
        lengh_matrix = load_length_matrix_from_file("src\\files\\floyd_washal_lenght.txt")

        temp = []
        origem = 340
        destino = 312
        
        # Print origin and destination station info
        print(vertices[origem-1].to_string())
        print(vertices[destino-1].to_string())
        
        # Print shortest path length (in minutes)
        now = datetime.now().time()
        print(f"Short lenght from {origem - 1} to {destino - 1}: {lengh_matrix[origem - 1][destino - 1]/AVERAGE_SPEED*60:.2f} minutes")
        short_path = get_short_path(vertices, predecessors, vertices[origem - 1],vertices[destino - 1])
        for index, current_vertex in enumerate(short_path):
            if index == 0:
                now = next_train_time(current_vertex.line, current_vertex.station_name, now, 0.0)
                print(f"{index+1} - {current_vertex.to_string()} - Next Train: {now.strftime("%H:%M:%S")}")
                continue
            
            previous_vertex = short_path[index-1]

            edge_found = None
            for edge in graph.adjacency_list.get(previous_vertex, []):
                if edge[0] == current_vertex:
                    edge_found = edge
                    break
            
            if edge_found:
                
                # If the third element has not None, it is a transfer (walked)
                if edge_found[2] != None:
                    print(f"{index+1} - {current_vertex.to_string()} - Walked")
                else:
                    travel_time = (lengh_matrix[index-1][index]/AVERAGE_SPEED)
                    now = next_train_time(current_vertex.line, current_vertex.station_name, now, travel_time)
                    print(f"{index+1} - {current_vertex.to_string()} - Next Train: {now.strftime("%H:%M:%S")}")
            else:
                print(f"{index+1} - {current_vertex.to_string()}")

    else:
        # If files do not exist, generate them
        generate_floyd_warshall()

