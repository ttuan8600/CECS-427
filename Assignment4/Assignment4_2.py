import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

def read_data(file_path):
    with open(file_path, 'r') as file:
        n = int(file.readline().strip())
        prices = list(map(int, file.readline().strip().split(',')))
        valuations = [list(map(int, line.strip().split(','))) for line in file]
    print(n)
    print(prices)
    print(valuations)
    return n, prices, valuations

def create_graph(n, prices, valuations):
    G = nx.Graph()
    buyers = [f"Buyer_{i+1}" for i in range(n)]
    houses = [f"House_{i+1}" for i in range(n)]
    G.add_nodes_from(buyers, bipartite=0)
    G.add_nodes_from(houses, bipartite=1)
    
    for i, buyer in enumerate(buyers):
        max_payoff = -float('inf')
        preferred_house = None
        
        for j, house in enumerate(houses):
            payoff = valuations[i][j] - prices[j]
            if payoff > max_payoff:
                max_payoff = payoff
                preferred_house = house
        
        G.add_edge(buyer, preferred_house)
        
    return G, buyers, houses

def visualize_graph(G, buyers, houses, assignments):
    pos = nx.bipartite_layout(G, buyers)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000)
    
    assigned_edges = [(f"Buyer_{buyer+1}", f"House_1") for buyer in assignments if assignments[buyer]['house'] == 0]
    nx.draw_networkx_edges(G, pos, edgelist=assigned_edges, edge_color='red', width=2)
    
    plt.show()

def preferred_seller_market_clearing(num_houses, house_prices, buyer_valuations):
    assignments = defaultdict(dict)
    remaining_houses = set(range(num_houses))
    remaining_buyers = set(range(num_houses))
    
    while remaining_buyers:
        buyer_to_preferred_seller = {}
        matched_houses = set()
        
        for buyer in remaining_buyers:
            max_payoff = -float('inf')
            preferred_seller = None
            
            for house in remaining_houses:
                payoff = buyer_valuations[buyer][house] - house_prices[house]
                if payoff > max_payoff:
                    max_payoff = payoff
                    preferred_seller = house
            
            buyer_to_preferred_seller[buyer] = preferred_seller
            print(f"Buyer_{buyer+1}'s preferred seller: House_{preferred_seller+1} with a payoff of {max_payoff}.")
        
        max_buyer_payoff = max(buyer_to_preferred_seller.keys(), key=(lambda k: buyer_valuations[k][buyer_to_preferred_seller[k]] - house_prices[buyer_to_preferred_seller[k]]))
        print(f"The buyer with the maximum payoff for their preferred seller is: Buyer_{max_buyer_payoff+1}")

        
        for buyer, house in buyer_to_preferred_seller.items():
            if house is not None and house not in matched_houses:
                assignments[buyer] = {'house': house, 'payoff': buyer_valuations[buyer][house] - house_prices[house]}
                remaining_houses.remove(house)
                remaining_buyers.remove(buyer)
                matched_houses.add(house)
                
    return assignments

def main():
    while True:
        file_name = input("Please enter the file name: ")
        if not file_name.endswith(".txt"):
            print("Warning: Please enter a valid .txt file.")
            continue
        try:
            n, prices, valuations = read_data(file_name)
            assignments = preferred_seller_market_clearing(n, prices, valuations)
            G, buyers, houses = create_graph(n, prices, valuations)
            visualize_graph(G, buyers, houses, assignments)
        except Exception as e:
            print(f"An error occurred while processing the file: {e}")
        rerun = input("\nDo you want to run the program again? (y/n): ").lower()
        if rerun != 'y':
            break

main()
