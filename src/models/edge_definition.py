from models.vertice_definition import vertice

"""
edge_definition.py
---------------------
Defines the edge class, representing a connection of two station in the subway graph.
A edge contains origin and destiny.
Includes methods for equality, hashing, and string representation.
"""

class edge:
    """
    Represents a connection of two station in the graph.
    Attributes:
        origin (vertice): Origin vertice of edge.
        ldestinyat (vertice): Destiny vertice of edge.
    """
    def __init__(self, origin:vertice, destiny: vertice):
        self.origin = origin
        self.destiny = destiny

    def __eq__(self, other):
        """
        Check equality with another edge based on origin and destiny.
        Args:
            other (edge): Another edge object.
        Returns:
            bool: True if IDs are equal, False otherwise.
        """
        if not isinstance(other, edge):
            return False
        return int(self.origin.id) == int(other.origin.id) and int(self.destiny.id) == int(other.destiny.id)

    def __hash__(self):
        """
        Compute hash based on origin and destiny ID.
        Returns:
            int: Hash value.
        """
        return hash(hash(self.origin), hash(self.destiny))

    def to_string(self):
        """
        Return edge information as a formatted string.
        Returns:
            str: String representation of the edge.
        """
        return f"Origin: {self.origin.id} - {self.origin.station_name} - {self.origin.line} | Destiny: {self.destiny.id} - {self.destiny.station_name} - {self.destiny.line}"
