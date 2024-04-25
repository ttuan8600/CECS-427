import networkx as nx
import json
import requests
from bs4 import BeautifulSoup
import collections
import matplotlib.pyplot as plt
import pickle
from networkx import draw, DiGraph, pagerank, spring_layout

# Global Constants
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}
MAX_SIZE = 750
MIN_SIZE = 100

# Retry file input if path invalid
def retry_enter_file(message, extension):
    print(f'Invalid file, please enter a path to a valid {extension} file\n')
    return input(message)

# read urls from txt file
def read_url():
    fileName = input("Enter path to plaintext file to read urls from: ")
    while True:
        if not fileName.endswith('.txt'):
            fileName = retry_enter_file("Enter path to plaintext file to read urls from: ", '.txt')
            continue
        try:
            with open(fileName, "r") as file:
                return [line.strip() for line in file if line.strip()]
        except Exception:
            fileName = retry_enter_file("Enter path to plaintext file to read urls from: ", '.txt')
            continue

def web_crawl(urls, LIMIT):
    urlQueue = urls.copy() # copy list of urls instead of modifying original list
    domain = urlQueue.pop(0)  # Assuming first URL is the domain
    graph = DiGraph() # build directed graph
    scrapedUrls = 0 

    while scrapedUrls < LIMIT and urlQueue:
            currentUrl = urlQueue.pop(0) # pop the first url from the queue
            if currentUrl in graph: # skipping processed urls
                continue
            response = requests.get(currentUrl, headers=HEADERS)
            # HTTP request to fetch content of page
            soup = BeautifulSoup(response.content, 'lxml')
            links = soup.find_all('a')
            scrapedUrls += 1
            print(f"Scraped {scrapedUrls}: {currentUrl}")
            
            # Loop each link found on the page
            for link in links:
                try:
                    href = link.get("href")
                    if not href.startswith('http'):
                        href = domain + href
                    elif not href.startswith(domain):
                        continue
                    if currentUrl != href and not href.startswith(currentUrl):
                    # add the link as edge in the graph
                        urlQueue.append(href)
                        if graph.number_of_nodes() < LIMIT:
                            graph.add_edge(currentUrl, href)
                        elif currentUrl in graph and href in graph:
                            graph.add_edge(currentUrl, href)
                except Exception as ex:
                    print(f'Error processing {currentUrl}: {ex}')
                    continue

    return graph

def plot_graph(graph):
    pos = spring_layout(graph, k=1.5)
    draw(graph, pos)
    plt.show()

# plot in degree distribution on log log scale
def loglog_plot(graph):
    degree_seq = sorted([d for n, d in graph.in_degree()], reverse=True)
    degreeCount = collections.Counter(degree_seq)
    deg, cnt = zip(*degreeCount.items())
    # sort, count occurrences, and make them seperate in degree value
    plt.loglog(deg, cnt, 'bo-')
    plt.title("Log-Log-Plot")
    plt.ylabel("Frequency")
    plt.xlabel("In-Degree")
    plt.show()

def r_graph():
    fileName = input("Enter path to pickle (.p) file to read graph from: ")
    while True:
        if not fileName.endswith('.p'):
            fileName = retry_enter_file("Enter path to pickle (.p) file to read graph from: ", '.p')
            continue
        try:
            with open(fileName, 'rb') as file:
                return pickle.load(file)
        except Exception:
            fileName = retry_enter_file("Enter path to pickle (.p) file to read graph from: ", '.p')
            continue

# calculate PageRank values
def p_rank(graph):
    pageRankDict = pagerank(graph)
    print('Writing pageranks to pageranks.txt')
    with open('pageRanks.txt', 'w') as outputFile:
        outputFile.write(json.dumps(pageRankDict))
    return pageRankDict

# filter nodes based on PageRank cutoffs
def cutoff_p_rank(graph, pageRankDict):
    maxPageRank = max(pageRankDict.values())
    minPageRank = min(pageRankDict.values())
    print('Max pagerank: ', maxPageRank)
    print('Min pagerank: ', minPageRank)

    while True:
        try:
            lowerRankLim = float(input('Enter lower rank cutoff for nodes: '))
            upperRankLim = float(input('Enter upper rank cutoff for nodes: '))
            if lowerRankLim >= upperRankLim or lowerRankLim < 0 or upperRankLim > 1:
                raise ValueError
            break
        except ValueError:
            print('Invalid value(s)')
            continue
    # filter nodes that do not meet the specified PageRank cutoff values.

    removeNodes = [n for n, d in pageRankDict.items() if not lowerRankLim <= d <= upperRankLim]
    graph.remove_nodes_from(removeNodes)

def plot_p_rank(graph, pageRankDict):
    maxPageRank = max(pageRankDict.values())
    minPageRank = min(pageRankDict.values())
    pos = spring_layout(graph, k=1.5)
    draw(graph, pos, node_size=[MIN_SIZE + ((pageRankDict[node] - minPageRank) / (maxPageRank - minPageRank)) * (MAX_SIZE - MIN_SIZE) for node in graph.nodes()],
         node_color=[((pageRankDict[node] - minPageRank) / (maxPageRank - minPageRank), 238/255, 144/255) for node in graph.nodes()])
    nx.draw_networkx_edges(graph, pos, edge_color='black', alpha=0.5)
    plt.show()

def main():
    while True:
        print("\nMenu:")
        print("1 - Web Crawl")
        print("2 - PageRank Analysis")
        print("0 - Exit")
        option = input("Please select an option: ")

        if option == '1':
            urls = read_url()
            LIMIT = int(input("Enter number of nodes to crawl: ")) 
            graph = web_crawl(urls, LIMIT)
            print('Crawling Successfully Completed\nTotal node count:', graph.number_of_nodes())

            writeFile = input('Enter .p file name to write representation of graph to: ')
            pickle.dump(graph, open(writeFile, 'wb'))

            plot_graph(graph)
            loglog_plot(graph)

        elif option == '2':
            graph = r_graph()
            pageRankDict = p_rank(graph)
            cutoff_p_rank(graph, pageRankDict)
            plot_p_rank(graph, pageRankDict)
        
        elif option == '0':
            break

        else:
            print("Invalid option, try again.")

if __name__ == "__main__":
    main()
