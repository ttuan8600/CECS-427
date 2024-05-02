import json
import pickle
import networkx as nx
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from networkx import draw, DiGraph, spring_layout, pagerank

# Global Constants
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 '
                  'Safari/537.36 '
}
MAX_SIZE = 750
MIN_SIZE = 100


# Retry file input if path invalid
def retry_enter_file(message):
    print(f'Invalid file, please enter a path to a valid file\n')
    return input(message)


# read urls from txt file
def read_url():
    fileName = input("Enter file name: ")
    while True:
        try:
            with open(fileName, "r") as file:
                lines = [line.strip() for line in file if line.strip()]
                n = int(lines[0])
                urls = lines[1:]
                return n, urls
        except Exception as e:
            print(f"Error: {e}")
            fileName = retry_enter_file("Re-enter file name: ")
            continue


def web_crawl(urls, n):
    urlQueue = urls.copy()  # copy list of urls instead of modifying original list
    domain = urlQueue.pop(0)  # Assuming first URL is the domain
    graph = DiGraph()  # build directed graph
    scrapedUrls = 0

    while scrapedUrls < n and urlQueue:
        currentUrl = urlQueue.pop(0)  # pop the first url from the queue
        if currentUrl in graph:  # skipping processed urls
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
                href = str(link.get("href"))
                if not href.startswith('http'):
                    href = domain + href
                elif not href.startswith(domain):
                    continue
                if currentUrl != href and not href.startswith(currentUrl):
                    # add the link as edge in the graph
                    urlQueue.append(href)
                    if graph.number_of_nodes() < n:
                        graph.add_edge(currentUrl, href, label=href)
                    elif currentUrl in graph and href in graph:
                        graph.add_edge(currentUrl, href, label=href)
            except Exception as ex:
                print(f'Error processing {currentUrl}: {ex}')
                continue
    return graph


def plot_graph(graph):

    pageRankDict = pagerank(graph)
    print('Writing pageranks to pageRanks.txt')
    with open('pageRanks.txt', 'w') as outputFile:
        outputFile.write(json.dumps(pageRankDict))

    pos = spring_layout(graph, k=1.5)
    draw(graph, pos)
    plt.show()


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
        
        
        
def main():
    n, urls = read_url()
    graph = web_crawl(urls, n)
    print('Crawling Successfully Completed!\nTotal node count:', graph.number_of_nodes())

    writeFile = input('Enter .p file name to write representation of graph to: ')
    save_graph(graph, writeFile)
    plot_graph(graph)


if __name__ == "__main__":
    main()
