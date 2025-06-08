from src.floyd_warshall.floyd_warshall import vertice, get_short_path

def load_vertices(filepath):
    """
    Load vertices from a given file.

    Reads the file line by line, splits each line by '@' delimiter,
    then further splits each vertex string by ';' to extract vertex data.

    Args:
        filepath (str): Path to the vertices file.

    Returns:
        list: A list of `vertice` objects created from the file data.
    """
    vertices = []
    with open(filepath, "r") as file:
        lines = file.readlines()
        for line in lines:
            records = line.strip().split("@")
            for r in records:
                if ";" in r:
                    v = r.split(";")
                    vertices.append(vertice(int(v[0]), float(v[1]), float(v[2]), v[3], v[4], int(v[5])))
    return vertices

def load_predecessors(filepath, vertices):
    """
    Load the predecessors matrix from a file.

    Reads the file line by line, splitting each line by '@' delimiter.
    Converts each predecessor entry into a `vertice` object or None.

    Args:
        filepath (str): Path to the predecessors file.
        vertices (list): List of vertices to relate predecessors to.

    Returns:
        list: A 2D list (matrix) of `vertice` objects or None representing predecessors.
    """
    predecessors = []
    with open(filepath, "r") as file:
        for line in file:
            row = []
            for v in line.strip().split("@"):
                if v == "None":
                    row.append(None)
                elif ";" in v:
                    p = v.split(";")
                    row.append(vertice(int(p[0]), float(p[1]), float(p[2]), p[3], p[4], int(p[5])))
            predecessors.append(row)
    return predecessors

# Re-export the get_short_path function from floyd_warshall module
get_short_path = get_short_path
