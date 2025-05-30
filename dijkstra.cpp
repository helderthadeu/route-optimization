#include <iostream>
#include <fstream>
#include <vector>
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

vector<vector<route>> get_graph(vector<route> routes, vector<int64_t> &vertices)
{
    cout << "Getting graph..." << endl;

    int size = vertices.size();
    vector<vector<route>> graph(size, vector<route>(size));

    for (const auto &r : routes)
    {
        int64_t start = r.start_node;
        int64_t end = r.end_node;

        // cout << "Route ID: " << r.id << " - Name: " << r.name << " - Start: " << start << " - End: " << end << endl;
        auto it_start = find(vertices.begin(), vertices.end(), start);
        auto it_end = find(vertices.begin(), vertices.end(), end);

        if (it_start != vertices.end() && it_end != vertices.end())
        {
            int j = distance(vertices.begin(), it_start);
            int k = distance(vertices.begin(), it_end);

            graph[j][k] = r;
            graph[k][j] = r;
        }
    }

    cout << "Graph generated!" << endl;
    return graph;
}

vector<vector<int64_t>> dijkstra(vector<vector<route>> graph, vector<int64_t> vertices, int64_t start)
{
    cout << "Dijkstra algorithm..." << endl;
    vector<vector<int64_t>> result(2, vector<int64_t>(vertices.size()));
    vector<bool> visited(vertices.size(), false);
    for (int i = 0; i < vertices.size(); i++)
    {
        result[0][i] = INF;
        result[1][i] = -1;
    }

    int start_idx = -1;
    for (int i = 0; i < vertices.size(); i++)
    {
        // cout << "Vertex: " << vertices[i] << " - Start: " << start << " - Equal: " <<  (vertices[i] == start)<< endl;
        if (vertices[i] == start)
        {
            cout << "Start index: " << i << endl;
            start_idx = i;
            visited[i] = true;
            result[0][i] = 0;
            break;
        }
    }

    if (start_idx == -1)
        return result;

    for (int count = 0; count < vertices.size() - 1; count++)
    {
        int64_t min = INF;
        int64_t min_index = -1, pred = -1;

        for (int i = 0; i < visited.size(); i++)
        {
            // cout <<i << " - Visited: " << visited[i]  << endl;
            if (visited[i])
            {

                // cout << "Visited: " << visited[i] << endl;
                for (int j = 0; j < vertices.size(); j++)
                {

                    // cout << j << " - Visited: " << i << " - Graph: " << graph[i][j].id << " - Length: " << graph[i][j].length << endl;
                    if (graph[i][j].id != 0 && result[0][i] + graph[i][j].length < min && !visited[j])
                    {

                        min_index = j;
                        pred = i;
                        min = result[0][i] + graph[i][j].length;
                        // cout << "Graph lenght: " << graph[i][j].length << " - Min: " << min << " - Min index: " << min_index << endl;
                    }
                }
            }

        }
        if (min_index == -1)
        {
            break; // Encerra se não houver nó válido para visitar
        }
        result[0][min_index] = min;
        result[1][min_index] = vertices[pred];
        // cout << "Min index: " << min_index << " - Min: " << min << endl;
        visited[min_index] = true;
    }
    int counter = 0;
    for(int i = 0; i < visited.size(); i++)
    {
        
        if (visited[i])
        {
            counter++;
        }
        
    }
    cout << "Visited: " << counter << " - Total: " << visited.size() << endl;
    return result;
}

void print_route(vector<route> routes)
{
    for (int i = routes.size() - 1; i > 0; i--)
    {
        cout << "Route: " << routes[i].id << " " << routes[i].name << " " << routes[i].ref << " " << routes[i].maxspeed << " - Lenght: " << routes[i].length << " - Begin: " << routes[i].start_node << " - End: " << routes[i].end_node << endl;
    }
}

void save_graph(vector<vector<route>> graph, int size, vector<int64_t> vertices)
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

        for (int j = 0; j < size; j++)
        {
            file << graph[i][j].id;
            if (j < size - 1)
                file << " ";
        }
        file << "\n";
    }
    cout << "Graph saved!" << endl;
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

    vector<vector<route>> graph;
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

    // print_route(routes);

    return 0;
}