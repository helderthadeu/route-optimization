#include <iostream>
#include <fstream>
#include <vector>
#include "include\\json.hpp"

using namespace std;
using json = nlohmann::json;

const int num_of_lines = INT_MAX;
const int INF = INT_MAX;

struct route
{
    int id;
    string name;
    string ref;
    int maxspeed;
    vector<int> nodes;
    double length;
    int start_node;
    int end_node;
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

    double dlong = (long_final - long_initial) * d2r;
    double dlat = (lat_final - lat_initial) * d2r;

    double temp_sin = sin(dlat / 2.0);
    double temp_cos = cos(lat_initial * d2r);
    double temp_sin2 = sin(dlong / 2.0);

    double a = (temp_sin * temp_sin) + (temp_cos * temp_cos) * (temp_sin2 * temp_sin2);
    double c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a));

    return 6368.1 * c;
}

double calc_geometry(json nodes, int size)
{
    double total_distance = 0.0;
    for (int i = 0; i < size - 1; i++)
    {

        total_distance += calc_distance(nodes[i]["lat"], nodes[i]["lon"], nodes[i + 1]["lat"], nodes[i + 1]["lon"]);
        // cout << "Distance: " << total_distance << endl;
    }
    return total_distance;
}

bool has_element(const vector<int> &vec, int element)
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

vector<route> define_routes(json data, vector<int> &vertices)
{
    vector<route> routes;

    for (int i = 0; i < data.size() && i < num_of_lines; i++)
    {
        route r;
        r.id = data[i].value("id", 0);

        if (data[i].contains("nodes"))
        {
            auto nodes = data[i]["nodes"];
            for (int j = 0; j < nodes.size(); j++)
            {
                r.nodes.push_back(nodes[j]);
                if (!has_element(vertices, nodes[j]))
                {
                    vertices.push_back(nodes[j]);
                }
            }
        }
        else
        {
            r.nodes.clear();
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
            r.length = calc_geometry(geometry, geometry.size());
        }
        else
        {
            r.length = 0;
        }
        routes.push_back(r);
    }

    return routes;
}

vector<vector<route>> get_graph(vector<route> routes, vector<int> &vertices)
{
    cout << "Getting graph..." << endl;

    int size = vertices.size();
    vector<vector<route>> graph(size, vector<route>(size)); // Grafo V x V

    for (const auto &r : routes)
    {
        int start = r.nodes.front();
        int end = r.nodes.back();

        // Encontra os índices de start e end nos vértices
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

void print_route(vector<route> routes)
{
    for (int i = routes.size() - 1; i > 0; i--)
    {
        cout << "Route: " << routes[i].id << " " << routes[i].name << " " << routes[i].ref << " " << routes[i].maxspeed << " - Lenght: " << routes[i].length << " - Begin: " << routes[i].start_node << " - End: " << routes[i].end_node << endl;
    }
}

void save_graph(vector<vector<route>> graph, int size)
{
    cout << "Saving graph..." << endl;
    ofstream file("files\\graph.txt");
    for (int i = 0; i < size; i++)
    {
        for (int j = 0; j < size; j++)
        {
            file << graph[i][j].id;
            if (j < size - 1)
                file << " "; // separa com espaço
        }
        file << "\n"; // nova linha após cada linha da matriz
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
    vector<int> vertices;
    vector<route> routes = define_routes(data, vertices);

    vector<vector<route>> graph;
    cout << "Vertices size: " << vertices.size() << endl;
    graph = get_graph(routes, vertices);

    save_graph(graph, vertices.size());
    // print_route(routes);

    return 0;
}