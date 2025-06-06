"""
vertice_definition.py
---------------------
Defines the vertice class, representing a station or node in the subway graph.
A vertice contains identifying information, coordinates, line, and complex ID.
Includes methods for equality, hashing, printing, and string representation.
"""

class vertice:
    """
    Represents a subway station or node in the graph.
    Attributes:
        id (int): Unique identifier for the vertice.
        lat (float): Latitude coordinate.
        lon (float): Longitude coordinate.
        station_name (str): Name of the station.
        line (str): Subway line name or code.
        complex_id (int): Identifier for station complexes (for transfers).
    """
    def __init__(self, id:int, lat:float, lon:float, station_name:str, line:str, complex_id:int):
        # Initialize vertice attributes
        self.id = id
        self.lat = lat
        self.lon = lon
        self.station_name = station_name
        self.line = line
        self.complex_id = complex_id
    
    def __eq__(self, other):
        """
        Check equality with another vertice based on ID.
        Args:
            other (vertice): Another vertice object.
        Returns:
            bool: True if IDs are equal, False otherwise.
        """
        if not isinstance(other, vertice):
            return False
        return int(self.id) == int(other.id)

    def __hash__(self):
        """
        Compute hash based on vertice ID (for use in sets and dicts).
        Returns:
            int: Hash value.
        """
        return hash(int(self.id))
        
    def print(self):
        """
        Print vertice information in a readable format.
        """
        print(f"Coordinates: {self.lat}, {self.lon} - Line: {self.line} - ID: {self.id} - Name: {self.station_name} - Complex ID: {self.complex_id}")
    
    def to_string(self):
        """
        Return vertice information as a formatted string.
        Returns:
            str: String representation of the vertice.
        """
        return f"Coordinates: {self.lat}, {self.lon} - Line: {self.line} - ID: {self.id} - Name: {self.station_name} - Complex ID: {self.complex_id}"
