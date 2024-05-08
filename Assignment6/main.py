import json
import random
import neal
import collections
import networkx as nx
import numpy as np
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
                source = parts[0]
                target = parts[1]

                G.add_edge(source, target)
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
    pos = nx.circular_layout(karate_graph)
    nx.draw(karate_graph, pos, with_labels=True, node_color='lightblue', edge_color='gray')
    plt.title("Karate Club Graph")
    plt.show()
    return karate_graph


# Creates a random bipartite graph with node sets A and B and edge (u, v) exists with probability p where u in A and v in B.def create_bipartite_graph(n, m, p):
def create_bipartite_graph(n, m, p):
    while True:
        G = nx.bipartite.random_graph(n, m, p)
        if nx.is_connected(G):
            return G


# Market clearing with the given file format.
def market_clearing(filename):
    valuations = []
    with open(filename, 'r') as file:
        # Parse file contents
        line = file.readline()
        n = int(line.strip().split(" ")[0])
        prices = list(map(int, line.strip().split(" ")[1].split(",")))

        lines = file.readlines()
        for line in lines:
            values = list(map(int, line.strip().split(',')))
            valuations.append(values)
    # Print the parsed data (optional)
    # print(n)
    # print(prices)
    # print(valuations)
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
def compute_perfect_matching(G):
    try:
        matching = nx.bipartite.maximum_matching(G)
        if len(matching) == len(G.nodes()):
            return matching, None, None
        else:
            left_nodes, right_nodes = nx.bipartite.sets(G)

            for side, node_set in [("Left", left_nodes), ("Right", right_nodes)]:
                neighbors = set()
                for node in node_set:
                    neighbors.update(G.neighbors(node))
                if len(neighbors) < len(node_set):
                    return None, list(node_set), side
            return None, list(G.nodes()), "Both"
    except nx.NetworkXError as e:
        return None, G.nodes()


# Compute the preferred-seller graph and output the final assignment (price and payoff of each buyer)
def compute_preferred_seller(n, prices, valuations):
    G = nx.Graph()
    buyers = [f"Buyer{i + 1}" for i in range(n)]
    houses = [f"House{i + 1}" for i in range(n)]
    G.add_nodes_from(buyers, bipartite=0)
    G.add_nodes_from(houses, bipartite=1)

    # Compute preferred seller for each buyer
    for i, buyer in enumerate(buyers):
        max_payoff = -np.max(valuations)
        preferred_house = None

        for j, house in enumerate(houses):
            payoff = valuations[i][j] - prices[j]
            if payoff > max_payoff:
                max_payoff = payoff
                preferred_house = house

        G.add_edge(buyer, preferred_house)

    # Compute assignments
    assignments = dict()
    remaining_houses = set(range(n))
    remaining_buyers = set(range(n))
    while remaining_buyers:
        buyer_to_preferred_seller = {}
        matched_houses = set()

        for buyer in remaining_buyers:
            max_payoff = -np.max(valuations)
            preferred_seller = None

            for house in remaining_houses:
                payoff = valuations[buyer][house] - prices[house]
                if payoff >= max_payoff:
                    max_payoff = payoff
                    preferred_seller = house

            buyer_to_preferred_seller[buyer] = preferred_seller

        for buyer, house in buyer_to_preferred_seller.items():
            if house is not None and house not in matched_houses:
                assignments[buyer] = {'house': house + 1, 'payoff': (valuations[buyer][house] - prices[house])}
                remaining_houses.remove(house)
                remaining_buyers.remove(buyer)
                matched_houses.add(house)

    print(assignments)
    return G, buyers, assignments


# Plot the graph G and highlighting the shortest path if provided
def plot_graph(G, bipartite, perfect_match, shortest, plot_shortest_path, plot_cluster_coefficient,
               plot_neighborhood_overlap):
    # check if the graph is a karate graph
    if bipartite:
        # assign location of nodes
        pos = nx.bipartite_layout(G, nodes=set(range(len(G) // 2)))

        # label the nodes
        labels = {}
        for node in G.nodes():
            labels[node] = f"A{node + 1}" if node < len(G) // 2 else f"B{node + 1 - len(G) // 2}"

        # draw graph
        nx.draw(G, pos, with_labels=True, labels=labels, node_color='lightblue', node_size=700)

        # label the edge if matching
        if perfect_match:
            matching_edges = [(k, v) for k, v in perfect_match.items() if k < v]
            nx.draw_networkx_edges(G, pos, edgelist=matching_edges, edge_color='black', style='dashed', width=3)
    else:
        pos = nx.spring_layout(G)
        # Draw the edges
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, edge_color='black')

        # # Draw the labels
        nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')

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

    # Show the plot
    plt.title("Graph Visualization")
    plt.axis('off')
    plt.show()


# Plot the preferred seller graph
def plot_preferred_seller_graph(G, buyers, assignments):
    pos = nx.bipartite_layout(G, buyers)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000)

    assigned_edges = [(f"Buyer{buyer + 1}", f"House{assignments[buyer]['house']}") for buyer in assignments]

    nx.draw_networkx_edges(G, pos, edgelist=assigned_edges, edge_color='black', style='dashed', width=3)

    plt.title("Preferred Seller Graph")
    plt.show()


# Plot the subgraph with all the nodes where the PageRank is at least lower_bound and at most upper_bound
def plot_pagerank(G, pr, lower_bound, upper_bound):
    pageRankDict = nx.pagerank(G)
    with open('pageRanks.txt', 'w') as outputFile:
        outputFile.write(json.dumps(pageRankDict))

    filtered_nodes = [node for node, rank in pr.items() if lower_bound <= rank <= upper_bound]
    subgraph = G.subgraph(filtered_nodes)

    plt.figure(figsize=(12, 6))
    pos = nx.spring_layout(subgraph)
    nx.draw(subgraph, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=10, font_color='black')
    plt.title(f"Subgraph with PageRank between {lower_bound} and {upper_bound}")
    plt.show()


# plot in degree distribution on log log scale
def loglog_plot(G):
    degree_seq = sorted([d for n, d in G.in_degree()], reverse=True)
    degreeCount = collections.Counter(degree_seq)
    deg, cnt = zip(*degreeCount.items())
    # sort, count occurrences, and make them seperate in degree value
    plt.loglog(deg, cnt, 'bo-')
    plt.title("Log-Log-Plot")
    plt.ylabel("Frequency")
    plt.xlabel("In-Degree")
    plt.show()


def cascade(graph, initiators, threshold):
    # Create a set to keep track of influenced nodes
    influenced = set(initiators)
    
    # Initialize a queue with the initiators
    queue = list(initiators)
    
    while queue:
        current_node = queue.pop(0)
        neighbors = list(graph.neighbors(current_node))
        for neighbor in neighbors:
            if neighbor not in influenced and random.random() <= threshold:
                influenced.add(neighbor)
                queue.append(neighbor)
    
    # Plot the original graph with initiators
    
    pos = nx.circular_layout(graph)

    plt.figure(figsize=(12, 6))
    plt.subplot(121)
    nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=800)
    nx.draw_networkx_nodes(graph, pos, nodelist=initiators, node_color='red', node_size=800)
    plt.title('Original Graph with Initiators')

    # Plot the final graph with influenced nodes
    plt.subplot(122)
    nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=800)
    nx.draw_networkx_nodes(graph, pos, nodelist=list(influenced), node_color='green', node_size=800)
    plt.title('Final Graph with Influenced Nodes')

    plt.tight_layout()
    plt.show()


def covid(graph, p, lifespan, shelter, r):
    # Initialize SIR model states
    nodes = list(graph.nodes())
    susceptible = set(nodes)
    infected = set(random.sample(nodes, int(p * len(nodes))))
    susceptible -= infected
    recovered = set()

    # Track epidemic progression
    infected_count = [len(infected)]
    recovered_count = [0]
    susceptible_count = [len(susceptible)]

    for day in range(1, lifespan + 1):
        # Shelter-in-place measures
        edges_to_remove = random.sample(list(graph.edges()), int(shelter * len(graph.edges())))
        graph.remove_edges_from(edges_to_remove)

        # Vaccination
        vaccinated = random.sample(list(susceptible), int(r * len(susceptible)))
        susceptible -= set(vaccinated)

        # Spread of the disease
        new_infections = set()
        for node in infected:
            neighbors = set(graph.neighbors(node))
            infected_neighbors = neighbors.intersection(susceptible)
            for neighbor in infected_neighbors:
                # Adjust the infection rate here
                infection_rate = 0.5 + 0.3 * (len(infected) / len(nodes))
                if random.random() <= infection_rate:
                    new_infections.add(neighbor)

        for node in new_infections:
            susceptible.remove(node)
            infected.add(node)

        # Recovery
        new_recoveries = set()
        for node in infected:
            # Adjust the recovery rate here
            recovery_rate = 0.1 + 0.3 * (len(infected) / len(nodes))
            if random.random() <= recovery_rate:
                new_recoveries.add(node)

        for node in new_recoveries:
            infected.remove(node)
            recovered.add(node)

        # Track counts
        infected_count.append(len(infected))
        recovered_count.append(len(recovered))
        susceptible_count.append(len(susceptible))

    # Plot epidemic progression
    plt.figure(figsize=(12, 6))
    plt.plot(range(lifespan + 1), susceptible_count, label='Susceptible')
    plt.plot(range(lifespan + 1), infected_count, label='Infected')
    plt.plot(range(lifespan + 1), recovered_count, label='Recovered')
    plt.xlabel('Day')
    plt.ylabel('Number of Nodes')
    plt.title('Progression of COVID-19 Epidemic')
    plt.legend()
    plt.show()


def main():
    # Global variables to temporary hold the G graph and shortest path
    shortest = None
    graph = None
    bipartite = False
    assignments = None
    buyers = None
    perfect_match = None
    page_rank = None
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
                    shortest = None
                    print("Random Graph created successfully")
                # Throw any other errors
                except ValueError as e:
                    print(f"Error: {e}")
                except Exception as e:
                    print(f"Error: {e}")

            elif sub.lower() == "b":
                try:
                    graph = create_karate_graph()
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
                    bipartite = True
                    print("Bipartite Graph created successfully")
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
            print("F. PageRank")
            print("G. Cascade Effect")
            print("H. COVID-19")
            sub = input("Enter your choice (a/b/c/d/e/f/g/h): ")

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
                perfect_match, c_set, side = compute_perfect_matching(graph)
                print("Perfect match found: ", perfect_match)
                
            elif sub.lower() == "e":
                graph, buyers, assignments = compute_preferred_seller(n, prices, valuations)
                print("Preferred Seller Graph computed successfully ")
                
            elif sub.lower() == "f":
                page_rank = nx.pagerank(graph)
                print("PageRank computed successfully!")
                print("PageRank values:", page_rank)
            
            elif sub.lower() == "g":
                try:
                    l = []
                    m = int(input("Enter the number of initiators: "))
                    for i in range (m): 
                        x = int(input("Enter the node: "))
                        l.append(x)
                    print("Initiators: ", l)
                    q = float(input("Enter the threshold of the cascade: "))
                    cascade(graph.copy(), l, q)
                except ValueError as e:
                    print(f"Error: {e}")
                except Exception as e:
                    print(f"Error: {e}")
            
            elif sub.lower() == "h":
                try:
                    file_name = input("Enter the edgelist: ")
                    graph = nx.read_edgelist(file_name)
                    p = float(input("Enter the fraction of initially infected nodes: "))
                    lifespan = int(input("Enter the period days of the simulation: "))
                    shelter = float(input("Enter the fraction of edges that are not considered by the shelter-in-place: "))
                    r = float(input("Enter the vaccination rate: "))
                    covid(graph, p, lifespan, shelter, r)
             
                except ValueError as e:
                    print(f"Error: {e}")
                except Exception as e:
                    print(f"Error: {e}")
            
            else:
                print("Invalid input. Please try again.")

        elif choice == "6":
            print("Plotting Options:")
            print("A. Shortest Path")
            print("B. Cluster Coefficients")
            print("C. Neighborhood Overlaps")
            print("D. Bipartite Graph")
            print("E. Preferred-seller Graph")
            print("F. PageRank")
            print("G. Loglog")
            sub = input("Enter your choice (a/b/c/d/e/f/g): ")

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

                sub = input("Enter your choice (a/b/c/d/e/f/g): ")

            try:
                # Check if graph and shortest path is defined yet
                if 'graph' not in locals() or 'shortest' not in locals():
                    raise ValueError("Graph or shortest path is not defined.")
                if sub.lower() == "d" or sub.lower() == "f":
                    if sub.lower() == "f":
                        lowerBound = float(input('Enter lower rank cutoff for nodes: '))
                        upperBound = float(input('Enter upper rank cutoff for nodes: '))
                        if lowerBound >= upperBound or lowerBound < 0 or upperBound > 1:
                            raise ValueError
                        plot_pagerank(graph, page_rank, lowerBound, upperBound)
                    else:
                        plot_graph(graph, bipartite, perfect_match, shortest, plot_shortest_path, plot_cluster_coefficient,
                               plot_neighborhood_overlap)
                if sub.lower() == "e":
                    plot_preferred_seller_graph(graph, buyers, assignments)
                # if sub.lower() == "f":
                #     lowerBound = float(input('Enter lower rank cutoff for nodes: '))
                #     upperBound = float(input('Enter upper rank cutoff for nodes: '))
                #     if lowerBound >= upperBound or lowerBound < 0 or upperBound > 1:
                #         raise ValueError
                #     plot_pagerank(graph, page_rank, lowerBound, upperBound)
                if sub.lower() == "g":
                    loglog_plot(graph)
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
