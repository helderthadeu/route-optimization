from src.models.vertice_definition import vertice
"""
vertice_definition.py
---------------------
Defines the graph class, representing a subway.
graph contains a adjacency list with the each edge from vertices, with destiny vertice and distance value.
"""

class graph:
    
    """
    Represents a subway graph.
    Attributes:
        adjacency_list (dict[vertice:list[tuple[vertice, float]]]): dict with adjacency list for each vertice.
    """
    def __init__(self, adjacency_list: dict[vertice:list[tuple[vertice, float]]]):
        # Initialize graph attributes
        self.adjacency_list = adjacency_list
