import networkx as nx
import matplotlib.pyplot as plt
from numpy import log as ln


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
        p = c + (ln(n) / n)
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
        print(f"Shortest path from {source} to {target}: {path}")
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


# Plot the graph G and highlighting the shortest path if provided
def plot_graph(G, shortest=None):
    # Create a spring layout for the graph
    pos = nx.spring_layout(G)

    # Draw the nodes
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)

    # Draw the edges
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)

    # Highlight the shortest path if provided
    if shortest:
        edges = [(shortest[i], shortest[i + 1]) for i in range(len(shortest) - 1)]
        nx.draw_networkx_edges(G, pos, edgelist=edges, width=2.0, alpha=0.9, edge_color='black', style='dashed')

    # Draw the labels
    nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif')

    # Show the plot
    plt.title("Graph Visualization")
    plt.axis('off')
    plt.show()


def main():
    # Global variables to temporary hold the G graph and shortest path
    shortest = None
    graph = None

    # Loop until the user chose 'x' to exit
    while True:
        print("Menu:")
        print("1. Read a Graph")
        print("2. Save the Graph")
        print("3. Create a Random Graph")
        print("4. Shortest Path")
        print("5. Plot G")
        print("x. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            file_name = input("Enter file name: ")
            graph = read_graph(file_name)
            # Handle if graph is None or other error cases

        elif choice == "2":
            file_name = input("Enter file name: ")
            save_graph(graph, file_name)
            # Handle if graph is not defined or other error cases

        elif choice == "3":
            n = int(input("Enter number of nodes: "))
            c = float(input("Enter parameter c: "))
            graph = create_random_graph(n, c)
            # Handle invalid inputs or other error cases

        elif choice == "4":
            source = input("Enter source node: ")
            target = input("Enter target node: ")
            shortest = shortest_path(graph, source, target)
            # Handle if shortest_path is None or other error cases

        elif choice == "5":
            plot_graph(graph, shortest)
            # Handle if graph is not defined or other error cases

        elif choice.lower() == "x":
            return None

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
