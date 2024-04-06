import neal
import random
import networkx as nx
from numpy import log as ln
import dwave_networkx as dnx
import matplotlib.pyplot as plt
from dwave_networkx.algorithms import structural_imbalance
from networkx.algorithms.assortativity import attribute_assortativity_coefficient

sampler = neal.SimulatedAnnealingSampler()
dnx.set_default_sampler(sampler)  # set default sampler


# Read a graph from an external file in adjacency list format
def read_graph(file_name):
    try:
        # Create an empty graph
        G = nx.Graph()

        # Read the adjacency list from the file
        with open(file_name, 'r') as file:
            for line in file:
                # Remove comments and whitespace
                line = line.split('#')[0].strip()
                if line:
                    # Split the line into nodes
                    nodes = line.split()
                    source = nodes[0]
                    targets = nodes[1:]
                    # Add edges to the graph
                    for target in targets:
                        G.add_edge(source, target)
        # Return the graph G to main
        return G
    # Throw error for when file is not found
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return None
    # Throw error for when the program can't read the graph from given file
    except Exception as e:
        print(f"Error reading graph from '{file_name}': {e}")
        return None


# Read a Digraph
def read_weighted_digraph(file_name):
    try:
        # Create an empty graph
        G = nx.DiGraph()

        # Read the adjacency list from the file
        with open(file_name, 'r') as file:
            for line in file:
                parts = line.strip().split()
                source = int(parts[0])
                target = int(parts[1])
                a = int(parts[2])
                b = int(parts[3])
                G.add_edge(source, target, weight=(a, b))
        return G
    # Throw error for when file is not found
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return None
    # Throw error for when the program can't read the graph from given file
    except Exception as e:
        print(f"Error reading graph from '{file_name}': {e}")
        return None


# Write the graph to an external file in adjacency list format
def save_graph(G, file_name):
    try:
        # Write the graph to the file in adjacency list format
        if isinstance(G, nx.DiGraph):
            # Directed graph
            nx.write_weighted_edgelist(G, file_name)
        elif isinstance(G, nx.Graph):
            # Undirected graph
            nx.write_edgelist(G, file_name, data=False)
        else:
            print("Graph type not supported.")
        print(f"Graph saved to '{file_name}' successfully.")
    # Throw error when fail to save the graph
    except Exception as e:
        print(f"Error saving graph to '{file_name}': {e}")


# Create an Erdos-Renyi random graph with n nodes and probability p = c+(ln(n)/ n)
def create_random_graph(n, c):
    try:
        # Set up p
        p = c * (ln(n) / n)
        # Create an Erdos-Renyi graph with n and p
        G = nx.erdos_renyi_graph(n, p)
        print(f"Erdos-Renyi random graph with {n} nodes created successfully.")
        # Return the graph G to main
        return G
    except Exception as e:
        print(f"Error creating random graph: {e}")
        return None


# Create a karate graph
def create_karate_graph():
    # Create the Karate Club graph
    karate_graph = nx.karate_club_graph()

    # Plot the graph
    pos = nx.spring_layout(karate_graph)
    nx.draw(karate_graph, pos, with_labels=True, node_color='lightblue', edge_color='gray')
    plt.title("Karate Club Graph")
    plt.show()


# Creates a random bipartite graph with node sets A and B and edge (u, v) exists with probability p where u in A and v in B.def create_bipartite_graph(n, m, p):
def create_bipartite_graph(n, m, p):
    G = nx.Graph()
    G.add_nodes_from(range(n), bipartite=0)  # Set nodes in A to bipartite 0
    G.add_nodes_from(range(n, n + m), bipartite=1)  # Set nodes in B to bipartite 1
    for u in range(n):
        for v in range(n, n + m):
            if random.random() < p:
                G.add_edge(u, v)

    # nx.draw(G, with_labels=True)
    # plt.show()
    return G


# Market clearing with the given file format.
def market_clearing(filename):
    # with open(filename, 'r') as file:
    #     lines = file.readlines()
    #     n = int(lines[0].split()[0])
    #     prices = list(map(int, lines[1].split(',')))
    #     valuations = [list(map(int, line.split(','))) for line in lines[2:]]
    #
    # print(n)
    # print(prices)
    # print(valuations)

    # Read file
    valuations = []
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Parse file contents
    n = int(file.readline().strip())
    prices = list(map(int, lines[1].strip().split(',')))

    for line in lines[2:]:
        valuations.append(list(map(int, line.strip().split(','))))

    # Print the parsed data (optional)
    print(n)
    print(prices)
    print(valuations)
    return n, prices, valuations


# Find the shortest path between source and target nodes in graph G
def shortest_path(G, source, target):
    try:
        # Compute the shortest path
        path = nx.shortest_path(G, source=int(source), target=int(target))
        return path
    # Throw error when there are no path between the source and target
    except nx.NetworkXNoPath:
        print(f"No path found from {source} to {target}.")
        return None
    # Throw error when nodes are not found
    except nx.NodeNotFound:
        print(f"Node {source} or {target} not found in the graph.")
        return None
    # Throw error when the program can't find the shortest path
    except Exception as e:
        print(f"Error computing shortest path: {e}")
        return None


def partition_graph(G, num_components):
    try:
        # cur_num_connected = nx.number_connected_components(G)
        # print(f"Graph has initially {cur_num_connected} connected components.")
        edges_removed = 0
        while nx.number_connected_components(G) < num_components:
            edge_betweenness = nx.edge_betweenness_centrality(G)
            max_betweenness_edge = max(edge_betweenness, key=edge_betweenness.get)
            G.remove_edge(*max_betweenness_edge)
            edges_removed += 1

        print(f"Removed {edges_removed} edges")
        print(f"Graph partitioned into {num_components} components.")
        return G
    except Exception as e:
        print(f"Error partitioning graph: {e}")
        return None


def find_equilibrium(G, n, source, destination):
    # Calculate the shortest paths for all pairs of nodes
    all_shortest_paths = dict(nx.all_pairs_dijkstra_path(G))

    # Calculate the social optimum
    social_optimum = sum([len(all_shortest_paths[source][destination]) - 1 for _ in range(n)])

    # Calculate the Nash equilibrium
    nash_equilibrium = len(all_shortest_paths[source][destination]) - 1

    return social_optimum, nash_equilibrium


# Computes the perfect matching in the given graph
def compute_perfect_matching(graph):
    matching = nx.bipartite.maximum_matching(graph)
    return matching


# Compute the preferred-seller graph and output the final assignment (price and payoff of each buyer)
def compute_preferred_seller(n, prices, valuations):
    assignments = dict()
    remaining_houses = set(range(n))
    remaining_buyers = set(range(n))
    while remaining_buyers:
        buyer_to_preferred_seller = {}
        matched_houses = set()

        for buyer in remaining_buyers:
            max_payoff = -float('inf')
            preferred_seller = None

            for house in remaining_houses:
                payoff = valuations[buyer][house] - prices[house]
                if payoff > max_payoff:
                    max_payoff = payoff
                    preferred_seller = house

            buyer_to_preferred_seller[buyer] = preferred_seller
            print(f"Buyer_{buyer + 1}'s preferred seller: House_{preferred_seller + 1} with a payoff of {max_payoff}.")

        max_buyer_payoff = max(buyer_to_preferred_seller.keys(), key=(
            lambda k: valuations[k][buyer_to_preferred_seller[k]] - prices[buyer_to_preferred_seller[k]]))
        print(f"The buyer with the maximum payoff for their preferred seller is: Buyer_{max_buyer_payoff + 1}")

        for buyer, house in buyer_to_preferred_seller.items():
            if house is not None and house not in matched_houses:
                assignments[buyer] = {'house': house, 'payoff': valuations[buyer][house] - prices[house]}
                remaining_houses.remove(house)
                remaining_buyers.remove(buyer)
                matched_houses.add(house)

    return assignments


# Plot the graph G and highlighting the shortest path if provided
def plot_graph(G, bipartite, shortest, plot_shortest_path, plot_cluster_coefficient, plot_neighborhood_overlap):
    # check if the graph is a karate graph
    if bipartite:
        nx.draw(G, with_labels=True)
        plt.show()
    else:
        pos = nx.spring_layout(G)

    # Draw the nodes
    node_sizes = []
    node_colors = []

    if plot_cluster_coefficient:
        cluster_coeffs = nx.clustering(G)
        cluster_min = min(cluster_coeffs.values())
        cluster_max = max(cluster_coeffs.values())

    for node in G.nodes():
        if plot_cluster_coefficient:
            cv = cluster_coeffs[node]
            pv = (cv - cluster_min) / (cluster_max - cluster_min)
            min_pixel = 200
            max_pixel = 800
            size = min_pixel + pv * (max_pixel - min_pixel)  # Adjust size based on cluster coefficient

            # RGB color based on cluster coefficient
            red = int(pv * 254)
            green = 254
            blue = 0
            color = '#%02x%02x%02x' % (red, green, blue)
        else:
            size = 500
            color = 'lightblue'
        node_sizes.append(size)
        node_colors.append(color)

    # Draw the nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes)

    edge_sizes = []
    edge_colors = []
    # Highlight neighborhood overlap if option is enabled
    if plot_neighborhood_overlap:
        overlaps = {}
        for edge in G.edges():
            src, dest = edge
            src_neighbors = set(G.neighbors(src))
            dest_neighbors = set(G.neighbors(dest))
            overlap = len(src_neighbors.intersection(dest_neighbors))
            overlaps[edge] = overlap

        overlap_min = min(overlaps.values())
        overlap_max = max(overlaps.values())
        for edge in G.edges():
            pv = (overlaps[edge] - overlap_min) / (overlap_max - overlap_min)
            # Adjust size of edges based on overlapping
            min_size = 1
            max_size = 10
            edge_size = min_size + pv * (max_size - min_size)
            # RGB color based on cluster coefficient
            red = int(pv * 254)
            green = 254
            blue = 0
            edge_color = '#%02x%02x%02x' % (red, green, blue)
            edge_sizes.append(edge_size)
            edge_colors.append(edge_color)

        nx.draw_networkx_edges(G, pos, width=edge_sizes, edge_color=edge_colors)
    # Highlight the shortest path if provided and option is enabled
    if shortest and plot_shortest_path:
        edges = [(shortest[i], shortest[i + 1]) for i in range(len(shortest) - 1)]
        nx.draw_networkx_edges(G, pos, edgelist=edges, width=2.0, alpha=0.9, edge_color='black', style='dashed')

    # Draw the edges
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, edge_color='black')

    # Draw the labels
    nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')

    # Show the plot
    plt.title("Graph Visualization")
    plt.axis('off')
    plt.show()


# Plot the preferred seller graph
def plot_preferred_seller_graph(assignments):
    G = nx.Graph()
    for buyer, assignment in assignments.items():
        G.add_edge(f"Buyer_{buyer + 1}", f"House_{assignment['house'] + 1}", payoff=assignment['payoff'])

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    edge_labels = nx.get_edge_attributes(G, 'payoff')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.show()


def main():
    # Global variables to temporary hold the G graph and shortest path
    shortest = None
    graph = None
    assignments = None
    n, prices, valuations = None, None, None
    plot_shortest_path = False
    plot_cluster_coefficient = False
    plot_neighborhood_overlap = False
    # Loop until the user chose 'x' to exit
    while True:
        print("Menu:")
        print("1. Read a Graph")
        print("2. Read a Digraph")
        print("3. Save the Graph")
        print("4. Create a Graph")
        print("5. Algorithms")
        print("6. Plot G")
        print("x. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            try:
                file_name = input("Enter file name: ")
                graph = read_graph(file_name)
                # Check if the graph exist
                if graph is None:
                    print("Error: Unable to read graph from file.")
                else:
                    print("Graph successfully read.")
                # Reset shortest path prevent errors with other graph
                karate = False
                shortest = None
            # Throw any other errors
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "2":
            try:
                file_name = input("Enter file name: ")
                graph = read_weighted_digraph(file_name)
                # Check if the graph exist
                if graph is None:
                    print("Error: Unable to read graph from file.")
                else:
                    print("Graph successfully read.")
                # Reset shortest path prevent errors with other graph
                karate = False
                shortest = None
                # Throw any other errors
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "3":
            try:
                # Check if graph is ready to save
                if 'graph' not in locals():
                    raise ValueError("Graph is not defined.")
                file_name = input("Enter file name: ")
                save_graph(graph, file_name)
                print("Graph saved successfully.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "4":
            print("What type of graph:")
            print("A. Random Erdos-Renyi Graph")
            print("B. Karate-Club Graph")
            print("C. Bipartite Graph")
            print("D. Market-clearing")
            sub = input("Enter your choice (a/b/c/d): ")
            if sub.lower() == "a":
                try:
                    n = int(input("Enter number of nodes: "))
                    c = float(input("Enter parameter c: "))
                    # Check if n or c is negative
                    if n <= 0 or c <= 0:
                        raise ValueError("Invalid inputs. Number of nodes n and parameter c must be positive.")
                    graph = create_random_graph(n, c)
                    # Reset shortest path prevent errors with other graph
                    karate = False
                    shortest = None
                # Throw any other errors
                except ValueError as e:
                    print(f"Error: {e}")
                except Exception as e:
                    print(f"Error: {e}")

            elif sub.lower() == "b":
                try:
                    create_karate_graph()
                    print("Karate-Club Graph created successfully")
                except Exception as e:
                    print(f"Error:{e}")
            elif sub.lower() == "c":
                try:
                    n = int(input("Enter number of nodes in set A: "))
                    m = int(input("Enter number of nodes in set B: "))
                    p = float(input("Enter probability of edge (u,v): "))
                    # Check if n or m is negative
                    if n <= 0 or m <= 0:
                        raise ValueError("Invalid inputs. Number of nodes n and m must be positive.")
                    graph = create_bipartite_graph(n, m, p)
                    # Reset shortest path prevent errors with other graph
                    shortest = None
                # Throw any other errors
                except ValueError as e:
                    print(f"Error: {e}")
                except Exception as e:
                    print(f"Error: {e}")
            elif sub.lower() == "d":
                file_name = input("Enter file name: ")
                n, prices, valuations = market_clearing(file_name)
            else:
                print("Invalid choice. Please try again.")

        elif choice == "5":
            print("Algorithms:")
            print("A. Shortest-Path")
            print("B. Partition G")
            print("C. Travel Equilibrium and Social Optimality")
            print("D. Perfect Matching")
            print("E. Preferred-seller Graph")
            sub = input("Enter your choice (a/b/c/d/e): ")

            if sub.lower() == "a":
                try:
                    if 'graph' not in locals():
                        raise ValueError("Graph is not defined.")
                    source = input("Enter source node: ")
                    target = input("Enter target node: ")
                    shortest = shortest_path(graph, source, target)
                    if shortest is None:
                        print("Error: No shortest path found.")
                    else:
                        print(f"Shortest path from {source} to {target}: {shortest}")
                except ValueError as e:
                    print(f"Error: {e}")
                except Exception as e:
                    print(f"Error: {e}")

            elif sub.lower() == "b":
                try:
                    if 'graph' not in locals():
                        raise ValueError("Graph is not defined.")
                    num_components = int(input("Enter number of components: "))
                    part = partition_graph(graph, num_components)
                    graph = part
                except ValueError as e:
                    print(f"Error: {e}")
                except Exception as e:
                    print(f"Error: {e}")

            elif sub.lower() == "c":
                try:
                    if 'graph' not in locals():
                        raise ValueError("Graph is not defined.")
                    n = int(input("Enter number of drivers: "))
                    source = int(input("Enter the initial node: "))
                    destination = int(input("Enter the destination node: "))
                    social_optimum, nash_equilibrium = find_equilibrium(graph, n, source, destination)
                except ValueError as e:
                    print(f"Error: {e}")
                except Exception as e:
                    print(f"Error: {e}")
            elif sub.lower() == "d":
                perfect_match = compute_perfect_matching(graph)
            elif sub.lower() == "e":
                assignments = compute_preferred_seller(n, prices, valuations)
            else:
                print("Invalid choice. Please try again.")

        elif choice == "6":
            print("Plotting Options:")
            print("A. Shortest Path")
            print("B. Cluster Coefficients")
            print("C. Neighborhood Overlaps")
            print("D. Bipartite Graph")
            print("E. Preferred-seller Graph")
            sub = input("Enter your choice (a/b/c/d/e): ")

            while sub.lower() != "d" and sub.lower() != "e":
                if sub.lower() == "a":
                    plot_shortest_path = not plot_shortest_path
                    if plot_shortest_path:
                        print("\n>> Shortest Path enabled!\n")
                    else:
                        print("\n>> Shortest Path disabled!\n")
                elif sub.lower() == "b":
                    plot_cluster_coefficient = not plot_cluster_coefficient
                    if plot_cluster_coefficient:
                        print("\n>> Cluster Coefficients enabled!\n")
                    else:
                        print("\n>> Cluster Coefficients disabled!\n")
                elif sub.lower() == "c":
                    plot_neighborhood_overlap = not plot_neighborhood_overlap
                    if plot_neighborhood_overlap:
                        print("\n>> Neighborhood Overlaps enabled!\n")
                    else:
                        print("\n>> Neighborhood Overlaps disabled!\n")
                else:
                    print("Invalid choice. Please try again.")

                sub = input("Enter your choice (a/b/c/d/e): ")

            try:
                # Check if graph and shortest path is defined yet
                if 'graph' not in locals() or 'shortest' not in locals():
                    raise ValueError("Graph or shortest path is not defined.")
                if sub.lower() == "d":
                    plot_graph(graph, True, shortest, plot_shortest_path, plot_cluster_coefficient,
                               plot_neighborhood_overlap)
                elif sub.lower() == "e":
                    plot_preferred_seller_graph(assignments)
                print("Graph plotted.")
            # Throw any other errors
            except ValueError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Error: {e}")

        elif choice.lower() == "x":
            return None

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
