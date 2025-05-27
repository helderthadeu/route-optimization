#include <iostream>
#include <fstream>
#include <queue>
#include <vector>
#include <set>
#include "include\\json.hpp"

using namespace std;
using json = nlohmann::json;

const int num_of_lines = INT_MAX;
// const int num_of_lines = 20;

const int64_t INF = LONG_MAX;

struct route
{
    int id;
    int64_t id_street;
    string name;
    string ref;
    int maxspeed;
    double length;
    int64_t start_node;
    int64_t end_node;
    double cordinates_start[2];
    double cordinates_end[2];
};

struct compare_routes
{
    bool operator()(const route &a, const route &b) const
    {
        return a.length < b.length;
    }
};

json load_data(const string &file_path)
{
    json data;

    ifstream file(file_path);

    if (!file.is_open())
    {
        cerr << "Error to open file!";
        cout << "Error to open file!";
    }

    file >> data;

    return data;
}

double calc_distance(double lat_initial, double long_initial, double lat_final, double long_final)
{

    double d2r = 0.017453292519943295769236;

    double dlong_t = (long_final - long_initial) * d2r;

    double dlat = (lat_final - lat_initial) * d2r;

    double temp_sin = sin(dlat / 2.0);
    double temp_cos = cos(lat_initial * d2r);
    double temp_sin2 = sin(dlong_t / 2.0);

    double a = (temp_sin * temp_sin) + (temp_cos * temp_cos) * (temp_sin2 * temp_sin2);
    double c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a));

    return 6368100 * c;
}

double calc_geometry(double cordinates_start[], double cordinates_end[])
{
    double total_distance = 0.0;

    total_distance += calc_distance(cordinates_start[0], cordinates_start[1], cordinates_end[0], cordinates_end[1]);
    // cout << "Distance: " << total_distance << endl;

    return total_distance;
}

bool has_element(const vector<int64_t> &vec, int element)
{
    for (int i = 0; i < vec.size(); i++)
    {
        if (vec[i] == element)
        {
            return true;
        }
    }
    return false;
}

vector<route> define_routes(json data, vector<int64_t> &vertices)
{
    cout << "Defining routes..." << endl;
    vector<route> routes;
    int id = 1;

    for (int i = 0; i < data.size() && i < num_of_lines; i++)
    {
        route r;
        r.id = id++;
        r.id_street = data[i].value("id", 0);
        vector<int64_t> nodes_temp;
        vector<vector<double>> cordinates(2);

        if (data[i].contains("nodes"))
        {
            auto nodes = data[i]["nodes"];
            for (int j = 0; j < nodes.size(); j++)
            {
                int64_t node_value = nodes[j].get<int64_t>();
                nodes_temp.push_back(node_value);
                if (!has_element(vertices, node_value))
                {
                    vertices.push_back(node_value);
                }
            }
        }
        if (data[i].contains("tags"))
        {
            auto tags = data[i]["tags"];
            r.name = tags.value("name", "");
            r.ref = tags.value("ref", "");

            if (tags.contains("maxspeed"))
            {
                if (tags["maxspeed"].is_number())
                {
                    r.maxspeed = tags["maxspeed"];
                }
                else if (tags["maxspeed"].is_string())
                {
                    string maxspeed_str = tags["maxspeed"];

                    try
                    {
                        r.maxspeed = stoi(maxspeed_str);
                    }
                    catch (...)
                    {
                        r.maxspeed = 0;
                    }
                }
            }
            else
            {
                r.maxspeed = 0;
            }
        }
        else
        {
            r.name = "";
            r.ref = "";
            r.maxspeed = 0;
        }

        if (data[i].contains("geometry"))
        {
            json geometry = data[i]["geometry"];

            for (int j = 0; j < geometry.size(); j++)
            {
                // cout << "Geometry: " << geometry[j]["lat"].get<double>() << endl;

                cordinates[0].push_back(geometry[j]["lat"].get<double>());
                cordinates[1].push_back(geometry[j]["lon"].get<double>());
            }
        }
        else
        {
            r.length = 0;
        }

        for (int j = 0; j < nodes_temp.size() - 1; j++)
        {

            // cout << j<< " - Node: " << nodes_temp[j] << " - Node: " << nodes_temp[j + 1] << endl;
            r.start_node = nodes_temp[j];
            r.end_node = nodes_temp[j + 1];
            r.cordinates_start[0] = cordinates[0][j];
            r.cordinates_start[1] = cordinates[1][j];
            r.cordinates_end[0] = cordinates[0][j + 1];
            r.cordinates_end[1] = cordinates[1][j + 1];
            r.length = calc_geometry(r.cordinates_start, r.cordinates_end);

            routes.push_back(r);
        }
    }

    return routes;
}

vector<set<route, compare_routes>> get_graph(vector<route> routes, vector<int64_t> &vertices)
{
    cout << "Getting graph..." << endl;

    unordered_map<int64_t, int> node_to_index;
    for (int i = 0; i < vertices.size(); i++)
    {
        node_to_index[vertices[i]] = i;
    }

    vector<set<route, compare_routes>> graph(vertices.size());

    for (const auto &r : routes)
    {
        int64_t start = r.start_node;
        int64_t end = r.end_node;

        if (node_to_index.find(start) != node_to_index.end() &&
            node_to_index.find(end) != node_to_index.end())
        {

            int start_idx = node_to_index[start];
            int end_idx = node_to_index[end];

            graph[start_idx].insert(r);
            graph[end_idx].insert(r);
        }
    }

    cout << "Graph built successfully!" << endl;
    return graph;
}

vector<vector<int64_t>> dijkstra(const vector<set<route, compare_routes>> &graph, const vector<int64_t> &vertices, int64_t start)
{
    cout << "Generating Dijkstra algorithm..." << endl;

    unordered_map<int64_t, int> node_to_index;
    for (int i = 0; i < vertices.size(); i++)
    {
        node_to_index[vertices[i]] = i;
    }

    // Check if the start node exists in the graph
    if (node_to_index.find(start) == node_to_index.end())
    {
        return vector<vector<int64_t>>(2, vector<int64_t>(vertices.size(), INF));
    }

    vector<int64_t> distances(vertices.size(), INF);
    vector<int64_t> predecessors(vertices.size(), -1);
    vector<bool> visited(vertices.size(), false);

    priority_queue<pair<int64_t, int>, vector<pair<int64_t, int>>, greater<pair<int64_t, int>>> visit_queue;

    int start_idx = node_to_index[start];
    distances[start_idx] = 0;
    visit_queue.push({0, start_idx});

    while (!visit_queue.empty())
    {
        int w = visit_queue.top().second;
        visit_queue.pop();

        if (visited[w])
            continue;
        visited[w] = true;

        for (const auto &r : graph[w])
        {
            int64_t v_node = (r.start_node == vertices[w]) ? r.end_node : r.start_node;
            if (node_to_index.find(v_node) == node_to_index.end())
                continue;

            int v = node_to_index[v_node];
            int64_t new_dist = distances[w] + r.length;

            if (new_dist < distances[v])
            {
                distances[v] = new_dist;
                predecessors[v] = vertices[w];
                visit_queue.push({new_dist, v});
            }
        }
    }
    int counter = 0;
    for (int i = 0; i < visited.size(); i++)
    {

        if (visited[i])
        {
            counter++;
        }
    }
    cout << "Visited: " << counter << " - Total: " << visited.size() << endl;

    vector<vector<int64_t>> result(2);
    result[0] = distances;
    result[1] = predecessors;
    return result;
}

void print_route(vector<route> routes)
{
    for (int i = routes.size() - 1; i > 0; i--)
    {
        cout << "Route: " << routes[i].id << " " << routes[i].name << " " << routes[i].ref << " " << routes[i].maxspeed << " - Lenght: " << routes[i].length << " - Begin: " << routes[i].start_node << " - End: " << routes[i].end_node << endl;
    }
}

void save_graph(vector<set<route, compare_routes>> graph, int size, vector<int64_t> vertices)
{
    cout << "Saving graph and vertices..." << endl;
    ofstream file("files\\graph.txt");
    if (!file.is_open())
    {
        cerr << "Error to open file!";
        cout << "Error to open file!";
        return;
    }

    for (int i = 0; i < size; i++)
    {
        file << vertices[i];
        if (i < size - 1)
            file << " ";
    }
    file << "\n";
    for (int i = 0; i < size; i++)
    {
        for (const auto &r : graph[i])
        {
            file << r.id;
            file << " ";
        }
        file << "\n";
    }
    cout << "Graph saved!" << endl;
}

int64_t search_nearest(vector<set<route, compare_routes>> graph, double lat, double lon)
{

    cout << "Searching nearest..." << endl;

    int64_t min_index = -1;
    double min_distance = 0x7FFFFFFFFFFFFFFF; // Initialize to a very large value
    for (const auto &origin : graph)
    {
        for (const auto &r : origin)
        {
            double distance = calc_distance(r.cordinates_start[0], r.cordinates_start[1], lat, lon);
            if (distance < min_distance)
            {
                min_distance = distance;
                min_index = r.id_street; // Store the ID of the route
            }
        }
    }

    return min_index;
}

int main()
{
    // json raw = load_data("files\\data.json");
    json raw = load_data("files\\PadreEustaquio.json");
    if (raw.empty())
    {
        return 1;
    }
    auto data = raw["elements"];

    // cout << data[10];
    vector<int64_t> vertices;
    vector<route> routes = define_routes(data, vertices);

    vector<set<route, compare_routes>> graph;
    cout << "Vertices size: " << vertices.size() << endl;
    graph = get_graph(routes, vertices);
    save_graph(graph, vertices.size(), vertices);

    vector<vector<int64_t>> graph_result = dijkstra(graph, vertices, 62994618);
    cout << endl
         << endl;
    for (int i = 0; i < graph_result.size(); i++)
    {
        for (int j = 0; j < graph_result[i].size(); j++)
        {
            if (graph_result[i][j] == INF)
            {
                cout << "-1 ";
            }
            else
            {
                cout << graph_result[i][j] << " ";
            }
        }
        cout << endl
             << endl;
    }

    cout << "Start node: " << search_nearest(graph, -19.931642127520806, -43.99641440308367) << endl;

    // print_route(routes);

    return 0;
}