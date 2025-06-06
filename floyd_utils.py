from src.floyd_warshall.floyd_warshall import vertice, get_short_path

def load_vertices(filepath):
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

# Reexporta função
get_short_path = get_short_path
