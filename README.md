# Subway Graph Shortest Path Finder

This project provides tools to model a subway network as a graph, compute shortest paths between stations using the Floyd-Warshall algorithm, and interact with the data via a command-line interface (CLI).

## Features

- **Graph Construction:** Reads subway station and line data, builds a graph where each station is a node (vertice), and edges represent direct connections or transfers.
- **Floyd-Warshall Algorithm:** Computes shortest paths between all pairs of stations, storing both the distance matrix and the predecessor matrix for path reconstruction.
- **Persistence:** Saves and loads graph, vertices, distance, and predecessor matrices to/from files for fast reuse.
- **CLI Interface:** Allows users to query the shortest path between two stations and see the step-by-step traversal, including transfers.

## Project Structure

```
assets/                     # Static assets (e.g., CSS)
src/
  files/                    # Output files (graph, matrices, etc.)
  floyd_warshall/
    floyd_warshall.py       # Main graph and algorithm logic
    manage_files.py         # Functions for saving/loading graph and matrices
  models/
    vertice_definition.py   # Definition of the vertice (station) class
    edge_definition.py      # Definition of the edge (line) class
    graph_definition.py     # Definition of the graph (subway) class
  subway_files/             # Input data (CSV files for stations and lines)
  file_operate.py           # Functions for loading CSV and JSON data
  main_cli.py               # Command-line interface for shortest path queries
  next_train.py             # Functions to get the time of the next train from the station and line
app.py                      # App is the UI
floyd_utils                 # Support functions to UI
```

## How It Works

1. **Data Loading:** Reads station and line data from CSV files in `subway_files/`.
2. **Graph Building:** Constructs a graph where each station is a node, and edges represent direct subway connections or transfer possibilities.
3. **Shortest Path Calculation:** Uses the Floyd-Warshall algorithm to compute shortest paths and saves the results for future queries.
4. **CLI Usage:** The user can run the CLI to query the shortest path between any two stations by their indices.

## Usage

1. **Install Requirements:**
   - Python 3.10+
   - Install dependencies (e.g., `geopy`, `chardet`, `pandas`, `datetime`, `plotly`, `dash`):
     ```
     pip install geopy chardet pandas datetime plotly dash
     ```

2. **Run the CLI:**
   ```
   python app.py
   ```
   - On first run, the program will generate the graph and matrices from the CSV data.
   - On subsequent runs, it will load the precomputed files for fast queries.

## Debug
For debug, run the CLI: 
```
python src/main_cli.py
```
**Modify Query:**
   - Edit the `origem` and `destino` variables in `main_cli.py` to set the origin and destination station indices.

## File Descriptions

- **file_operate.py:** Functions to load CSV and JSON data with automatic encoding detection.
- **floyd_warshall.py:** Core logic for graph construction and the Floyd-Warshall algorithm.
- **manage_files.py:** Functions to save/load the graph, vertices, and matrices to/from files.
- **next_train.py:** Functions to get the time of the next train.
- **vertice_definition.py:** The `vertice` class, representing a subway station.
- **edge_definition.py:** The `edge` class, representing a line between two subway stations.
- **graph_definition.py:** The `graph` class, representing a subway of New York.
- **main_cli.py:** Command-line interface for querying shortest paths.
- **app.py:** Main file, execute the application

## Customization

- To add or update subway data, modify the CSV files in `subway_files/`.
- To change the speed or ticket price, edit the constants in the relevant files.

## License

This project is for educational purposes.
