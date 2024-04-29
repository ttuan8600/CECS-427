import scrapy
import matplotlib.pyplot as plt
from networkx import draw, DiGraph, spring_layout
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class Spidey(CrawlSpider):
