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
        origem = 1
        destino = 78
        
        # Print origin and destination station info
        print(vertices[origem].to_string())
        print(vertices[destino].to_string())
        
        # Print shortest path length (in minutes)
        print(f"Short lenght from {origem+1} to {destino+1}: {lengh_matrix[origem][destino]/AVERAGE_SPEED*60:.2f} minutes")
        short_path = get_short_path(vertices, predecessors, vertices[origem],vertices[destino])
        for index, current_vertex in enumerate(short_path):
            if index == 0:
                print(f"{index+1} - {current_vertex.to_string()}")
                continue
            
            previous_vertex = short_path[index-1]

            edge_found = None
            for edge in graph.get(previous_vertex, []):
                if edge[0] == current_vertex:
                    edge_found = edge
                    break
            
            if edge_found:
                # If the edge has a third element, it is a transfer (walked)
                if len(edge_found) > 2:
                    print(f"{index+1} - {current_vertex.to_string()} - walked")
                else:
                    print(f"{index+1} - {current_vertex.to_string()}")
            else:
                print(f"{index+1} - {current_vertex.to_string()}")
        
        # print(len(temp))
    else:
        # If files do not exist, generate them
        generate_floyd_warshall()

