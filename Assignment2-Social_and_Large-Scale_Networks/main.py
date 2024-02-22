import random
import networkx as nx
import matplotlib.pyplot as plt
from numpy import log as ln
from dwave_networkx.algorithms import structural_imbalance
from networkx.algorithms.assortativity import attribute_assortativity_coefficient
import dimod


sampler = dimod.ExactSolver()

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
        nodes = [str(i) for i in range(n)]  # Generate node names as strings from '0' to 'n-1'
        # Create an Erdos-Renyi graph with n and p
        G = nx.erdos_renyi_graph(n, p)
        # Create a mapping from old nodes to new nodes
        mapping = {old_node: new_node for old_node, new_node in zip(G.nodes(), nodes)}
        # Relabel the nodes using the mapping
        G = nx.relabel_nodes(G, mapping)
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
        path = nx.shortest_path(G, source=source, target=target)
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


def clustering_coefficients(G):
    try:
        cluster_coeffs = nx.clustering(G)
        cluster_min = min(cluster_coeffs.values())
        cluster_max = max(cluster_coeffs.values())

        colors = [(cluster_coeffs[node] - cluster_min) / (cluster_max - cluster_min) for node in G.nodes()]
        sizes = [100 + (cluster_coeffs[node] - cluster_min) / (cluster_max - cluster_min) * (500 - 100) for node in
                 G.nodes()]

        pos = nx.spring_layout(G)
        plt.figure(figsize=(10, 8))
        nx.draw(G, pos, with_labels=True, node_size=sizes, node_color=colors, cmap=plt.cm.Reds)
        plt.show()
    except Exception as exc:
        print(str(exc))


def partition_graph(G, num_components):
    try:
        for i in range(num_components):
            edge_betweenness = nx.edge_betweenness_centrality(G)
            max_betweenness_edge = max(edge_betweenness, key=edge_betweenness.get)
            G.remove_edge(*max_betweenness_edge)
        print(f"Graph removed {num_components} edges.")
        return G
    except Exception as e:
        print(f"Error partitioning graph: {e}")
        return None


def assign_homophily_attributes(G, p):
    try:
        # Assign colors (red or blue) to nodes independently with probability p
        for node in G.nodes():
            color = "red" if random.random() < p else "blue"
            G.nodes[node]["color"] = color

        # Check for assortativity (homophily)
        assortativity = attribute_assortativity_coefficient(G, "color")
        print(f"Assortativity coefficient: {assortativity}")
        # Checking if assortativity is close to p
        if abs(assortativity - p) < 0.1:  # Assuming a small threshold of 0.1
            print(f"The test returns a value similar to p: {p}")
        else:
            print(f"The test returns a value different from p: {p}")
        return G
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error assigning or validating attributes: {e}")


def assign_balanced_graph_attributes(G, p):
    try:
        # Assign signs (+ or -) to edges independently with probability p
        for edge in G.edges():
            sign = 1 if random.random() < p else -1
            G.edges[edge]["sign"] = sign

        # Check for structural imbalance using dwave_networkx
        frustrated_edges, colors = structural_imbalance(G, sampler)

        # Check if the graph is balanced
        if len(frustrated_edges) == 0:
            print("The graph is balanced.")
        else:
            print(f"The graph is not balanced. Number of frustrated edges: {len(frustrated_edges)}")
        return G
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error assigning or validating attributes: {e}")


# Plot the graph G and highlighting the shortest path if provided
def plot_graph(G, karate, shortest, plot_shortest_path, plot_cluster_coefficient, plot_neighborhood_overlap):
    # Create a spring layout for the graph
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

        # Draw the nodes and edges
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes)
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)

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

    # Draw the labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')

    # check and show karate graph with features that are enabled
    if karate:
        nx.draw_circular(G, with_labels=True)

    # Show the plot
    plt.title("Graph Visualization")
    plt.axis('off')
    plt.show()


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
                # Throw any other errors
                except ValueError as e:
                    print(f"Error: {e}")
                except Exception as e:
                    print(f"Error: {e}")

            elif sub.lower() == "b":
                try:
                    graph = nx.karate_club_graph()
                    karate = True
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
                    if part is not None:
                        pos = nx.spring_layout(part)
                        nx.draw(part, pos, with_labels=True)
                        plt.show()
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
                elif sub.lower() == "b":
                    plot_cluster_coefficient = not plot_cluster_coefficient
                elif sub.lower() == "c":
                    plot_neighborhood_overlap = not plot_neighborhood_overlap
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
                # Reset shortest path prevent errors with other graph
                karate = False
                shortest = None
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
                graph = assign_homophily_attributes(graph, p)

            elif sub == "b":
                p = float(input("Enter probability p (0-1): "))
                if p < 0 or p > 1:
                    raise ValueError("Probability p must be between 0 and 1.")
                graph = assign_balanced_graph_attributes(graph, p)

            else:
                print("Invalid sub-option. Please choose 'a' or 'b'.")

        elif choice.lower() == "x":
            return None

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
