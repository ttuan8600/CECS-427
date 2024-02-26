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


# Write the graph to an external file in adjacency list format
def save_graph(G, file_name):
    try:
        # Write the graph to the file in adjacency list format
        with open(file_name, 'w') as file:
            for node in G.nodes():
                neighbors = ' '.join(G.neighbors(node))
                file.write(f"{node} {neighbors}\n")
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


def assign_homophily_attributes(G, p, karate):
    try:
        # Assign colors (red or blue) to nodes independently with probability p
        assigned_colors = {node: 'red' if random.random() < p else 'blue' for node in G.nodes()}
        nx.set_node_attributes(G, assigned_colors, "color")
        color_map = [assigned_colors[node] for node in G.nodes()]

        # Check for assortativity (homophily)
        assortativity = attribute_assortativity_coefficient(G, "color")
        print(f"Assortativity coefficient: {assortativity}")

        # Checking if assortativity is close to p
        if abs(assortativity - p) < 0.1:  # Assuming a small threshold of 0.1
            print(f"The test returns a value similar to p: {p}")
        else:
            print(f"The test returns a value different from p: {p}")

        if karate:
            pos = nx.circular_layout(G)
        else:
            pos = nx.spring_layout(G)

        nx.draw(G, pos, with_labels=True, node_color=color_map)
        plt.show()
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error assigning or validating attributes: {e}")


def assign_balanced_graph_attributes(G, p, karate):
    try:
        # Assign signs (+ or -) to edges independently with probability p
        assigned_signs = {edge: 1 if random.random() < p else -1 for edge in G.edges()}
        nx.set_edge_attributes(G, assigned_signs, "sign")

        # Check for structural imbalance using dwave_networkx
        frustrated_edges, colors = structural_imbalance(G)

        # Visualization
        pos_edges = [edge for edge, sign in assigned_signs.items() if sign == 1]
        neg_edges = [edge for edge, sign in assigned_signs.items() if sign == -1]
        pos_labels = {edge: f"+" for edge in pos_edges}
        neg_labels = {edge: f"-" for edge in neg_edges}
        # Check if the graph is balanced
        if len(frustrated_edges) == 0:
            print("The graph is balanced.")
        else:
            print(f"The graph is not balanced. Number of frustrated edges: {len(frustrated_edges)}")

        if karate:
            pos = nx.circular_layout(G)
        else:
            pos = nx.spring_layout(G)

        nx.draw_networkx_nodes(G, pos, node_color='lightblue')
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos, width=1.5)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=pos_labels, font_color='red', font_weight='bold', font_size=12)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=neg_labels, font_color='blue', font_weight='bold',
                                     font_size=12)
        plt.title("Graph Visualization")
        plt.axis('off')
        plt.show()
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error assigning or validating attributes: {e}")


# Plot the graph G and highlighting the shortest path if provided
def plot_graph(G, karate, shortest, plot_shortest_path, plot_cluster_coefficient, plot_neighborhood_overlap):
    # check if the graph is a karate graph
    if karate:
        pos = nx.circular_layout(G)
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


def create_karate_graph():
    return nx.karate_club_graph()


def main():
    # Global variables to temporary hold the G graph and shortest path
    shortest = None
    graph = None
    karate = False
    plot_shortest_path = False
    plot_cluster_coefficient = False
    plot_neighborhood_overlap = False
    # Loop until the user chose 'x' to exit
    while True:
        print("Menu:")
        print("1. Read a Graph")
        print("2. Save the Graph")
        print("3. Create a Graph")
        print("4. Algorithms")
        print("5. Plot G")
        print("6. Assign and validate Attributes")
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
                # Check if graph is ready to save
                if 'graph' not in locals():
                    raise ValueError("Graph is not defined.")
                file_name = input("Enter file name: ")
                save_graph(graph, file_name)
                print("Graph saved successfully.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "3":
            print("What type of graph:")
            print("a. Random Erdos-Renyi Graph")
            print("b. Karate-Club Graph")
            sub = input("Enter your choice (a/b): ")
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
                    graph = create_karate_graph()
                    karate = True
                    shortest = None
                    print("Karate-Club Graph created successfully")
                except Exception as e:
                    print(f"Error:{e}")
            else:
                print("Invalid choice. Please try again.")

        elif choice == "4":
            print("Algorithms:")
            print("a. Shortest-Path")
            print("b. Partition G")
            sub = input("Enter your choice (a/b): ")

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

            else:
                print("Invalid choice. Please try again.")

        elif choice == "5":
            print("Plotting Options:")
            print("a. Shortest Path")
            print("b. Cluster Coefficients")
            print("c. Neighborhood Overlaps")
            print("g. Plot the graph")
            sub = input("Enter your choice (a/b/c/g): ")

            while sub.lower() != "g":
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

                sub = input("Enter your choice (a/b/c/g): ")
            try:
                # Check if graph and shortest path is defined yet
                if 'graph' not in locals() or 'shortest' not in locals():
                    raise ValueError("Graph or shortest path is not defined.")
                plot_graph(graph, karate, shortest, plot_shortest_path, plot_cluster_coefficient,
                           plot_neighborhood_overlap)
                print("Graph plotted.")
            # Throw any other errors
            except ValueError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "6":
            print("Assign and validate Attributes:")
            print("a. Homophily")
            print("b. Balanced Graph")
            sub = input("Enter your choice (a/b): ")
            if sub == "a":
                p = float(input("Enter probability p (0-1): "))
                if p < 0 or p > 1:
                    raise ValueError("Probability p must be between 0 and 1.")
                assign_homophily_attributes(graph, p, karate)

            elif sub == "b":
                p = float(input("Enter probability p (0-1): "))
                if p < 0 or p > 1:
                    raise ValueError("Probability p must be between 0 and 1.")
                assign_balanced_graph_attributes(graph, p, karate)

            else:
                print("Invalid sub-option. Please choose 'a' or 'b'.")

        elif choice.lower() == "x":
            return None

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
