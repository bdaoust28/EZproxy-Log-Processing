# Written by Beau Daoust (2021)
# custom-made script to manually retain project settings and to serve as a bridge between frontend.py and ezproxy_spider.py

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os

class SpiderScript:
    def __init__(self):
        from ezproxy.ezproxy.spiders.ezproxy_spider import EZproxySpider
        settings_file_path = 'ezproxy.ezproxy.script_settings' # path from venv (root) to script settings file
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path) # manually point to settings
        self.process = CrawlerProcess(get_project_settings())
        self.spider = EZproxySpider # specifies which spider to use

    def run(self):
        self.process.crawl(self.spider) # runs spider w/o terminal input
        self.process.start()

if __name__ == "__main__":
    print('\nTo use this script, run frontend.py or run from terminal instead. To do so...\n'
          '1. Navigate directory until cwd is ../LogProcessing/venv/ezproxy/ezproxy\n'
          '2. Type and run "scrapy crawl log" in terminal.')