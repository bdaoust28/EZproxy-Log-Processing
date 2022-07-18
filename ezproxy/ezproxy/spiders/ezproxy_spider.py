# Written by Beau Daoust (2021)
import scrapy, json2, json, sys, time, logging
import datetime as dt
from datetime import timedelta
from logwriter import login_log_action as log_action

class GetItem(scrapy.Item): # used for file retrieval and processing
    file_urls = scrapy.Field()
    files = scrapy.Field

class EZproxySpider(scrapy.Spider): # main spider
    creds = json2.load_file(f'{sys.path[0]}/ezproxy/ezproxy/creds.json')
    name = 'log'
    start_urls = [creds['crawlsite']] # spider begins here
    logging.getLogger('scrapy').propagate = False # turns off debug feed when spider is ran

    def parse(self, response):

        inputs = response.css('form input') # init form var to simulate user login
        formdata = {}
        for field in inputs:
            name = field.css('::attr(type)').get()
            value = field.css('::attr(value)').get()
            formdata[name] = value

        # admin credentials
        formdata['user'] = creds['ezp_user']
        formdata['pass'] = creds['ezp_pass']

        # submit form to site, call next function
        return scrapy.FormRequest.from_response(
            response,
            formdata=formdata,
            callback=self.parse_after_login
        )

    def parse_after_login(self, response):
        try:
            # check for failed login
            response.xpath('/html/body/p/strong').get().__contains__('incorrect')
            print('Login failed. Login credentials have likely been changed.')

            # add to history.log
            log_action('ezp_login')
        except AttributeError:
            # login success -- navigate to Log Listing hyperlink
            logList = response.xpath('/html/body/p[3]/a').attrib['href']
            logList = response.urljoin(logList)
            yield scrapy.Request(logList, callback=self.parse_log_list)

    def parse_log_list(self, response):
        # Navigated to Log Listing
        item = GetItem() # instance of GetItem class

        # get str of today's and tomorrow's date in YYYYMMDD format
        today = dt.date.today().strftime('%Y%m%d')
        tmr = dt.date.today() + timedelta(days=1)  # today plus 1 day
        tmr = tmr.strftime('%Y%m%d')

        # main event: log file search
        for logfile in response.xpath('/html/body/div/a'):
            # print(logfile.get())
            logLink = logfile.attrib['href']
            logLink = response.urljoin(logLink)

            # retrieve spu[date].log files up to day prior
            if logLink.__contains__('spu') and not logLink.__contains__(today) and not logLink.__contains__(tmr) and not logLink.__contains__('.gz'):
                item['file_urls'] = [logLink]
                yield item

            # retrieve [date].txt files up to day prior
            if logLink.__contains__('.txt') and not logLink.__contains__(today) and not logLink.__contains__(tmr) and not logLink.__contains__('messages'):
                item['file_urls'] = [logLink]
                yield item
if __name__ == "__main__":
    print('\nTo use this script, run frontend.py or run from terminal instead. To do so...\n1. Navigate directory until cwd is ../LogProcessing/venv/ezproxy/ezproxy\n2. Type and run "scrapy crawl log" in terminal.')