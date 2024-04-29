import scrapy
import matplotlib.pyplot as plt
from networkx import draw, DiGraph, spring_layout
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class Spidey(CrawlSpider):
    name = "mySpidey"
    allowed_domains = ["dblg.org"]
    start_urls = ["https://dblp.org/pid"]
    rules = (
        Rule(LinkExtractor(allow_domains=allowed_domains)),
    )