# import json
# import requests
# from bs4 import BeautifulSoup
import scrapy
from collections import defaultdict
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import matplotlib.pyplot as plt
import pickle
from networkx import draw, DiGraph, spring_layout

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


def parse_item(response, graph):
    from_url = response.request.headers.get('Referer', None).decode('utf-8') if response.request.headers.get('Referer', None) else None
    to_url = response.url
    if from_url and to_url not in graph[from_url]:
        graph[from_url].append(to_url)
        print(f"Added edge: {from_url} -> {to_url}")


def create_spider(domain, start_urls, n):
    graph = defaultdict(list)

    def spider_function(response):
        parse_item(response, graph)

    spider = CrawlSpider('my_spider', allowed_domains=[domain], start_urls=start_urls[:n])
    spider.parse_item = spider_function
    spider.rules = (Rule(LinkExtractor(allow_domains=[domain]), callback='parse_item', follow=True),)

    return spider, graph


def web_crawl(urls, n):
    # urlQueue = urls.copy()  # copy list of urls instead of modifying original list
    # domain = urlQueue.pop(0)  # Assuming first URL is the domain
    # graph = DiGraph()  # build directed graph
    # scrapedUrls = 0
    #
    # while scrapedUrls < n and urlQueue:
    #     currentUrl = urlQueue.pop(0)  # pop the first url from the queue
    #     if currentUrl in graph:  # skipping processed urls
    #         continue
    #     response = requests.get(currentUrl, headers=HEADERS)
    #     # HTTP request to fetch content of page
    #     soup = BeautifulSoup(response.content, 'lxml')
    #     links = soup.find_all('a')
    #     scrapedUrls += 1
    #     print(f"Scraped {scrapedUrls}: {currentUrl}")
    #
    #     # Loop each link found on the page
    #     for link in links:
    #         try:
    #             href = str(link.get("href"))
    #             if not href.startswith('http'):
    #                 href = domain + href
    #             elif not href.startswith(domain):
    #                 continue
    #             if currentUrl != href and not href.startswith(currentUrl):
    #                 # add the link as edge in the graph
    #                 urlQueue.append(href)
    #                 if graph.number_of_nodes() < n:
    #                     graph.add_edge(currentUrl, href)
    #                 elif currentUrl in graph and href in graph:
    #                     graph.add_edge(currentUrl, href)
    #         except Exception as ex:
    #             print(f'Error processing {currentUrl}: {ex}')
    #             continue
    # return graph
    with open(file_name, 'r') as file:
        n = int(file.readline().strip())
        domain = file.readline().strip()
        start_urls = [file.readline().strip() for _ in range(n)]

    spider, graph = create_spider(domain, start_urls, n)

    process = CrawlerProcess(get_project_settings())
    process.crawl(spider)
    process.start()


def plot_graph(graph):
    pos = spring_layout(graph, k=1.5)
    draw(graph, pos)
    plt.show()


def main():
    n, urls = read_url()
    graph = web_crawl(urls, n)
    print('Crawling Successfully Completed!\nTotal node count:', graph.number_of_nodes())

    writeFile = input('Enter .p file name to write representation of graph to: ')
    pickle.dump(graph, open(writeFile, 'wb'))

    plot_graph(graph)


if __name__ == "__main__":
    main()
