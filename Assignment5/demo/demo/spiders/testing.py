from collections import defaultdict

import scrapy
import matplotlib.pyplot as plt
from networkx import draw, DiGraph, spring_layout
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.project import get_project_settings


class Spidey(CrawlSpider):
    name = "mySpidey"
    allowed_domains = ["dblp.org"]
    start_urls = ["https://dblp.org/pid"]
    rules = (
        Rule(LinkExtractor(allow_domains=allowed_domains), callback='parse_item', follow=True),
    )

    def parse(self, response):
        for links in response.css('a'):
            yield {
                'link': links.css('a.').attrib['href'],
            }

