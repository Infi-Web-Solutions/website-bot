from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
import argparse,json

class UrlCrawlSpider(CrawlSpider):
    name = "RteSpider"
    def __init__(self, start_urls,allowed_domains,output_file, *a, **kw):
        super().__init__(*a, **kw)
        self.start_urls = start_urls
        self.allowed_domains = allowed_domains
        self.output_file = output_file
        self.results = []
    rules = [ Rule(LinkExtractor(allow=r'.*'), callback='parse_page', follow=True),]
    
    def parse_page(self, response):
        self.results.append(response.url)
    
    def close(self, reason):
        # Write results to the specified output file when the spider closes
        with open(self.output_file, 'w') as f:
            json.dump(self.results, f)

def main():
    parser = argparse.ArgumentParser(description='Scrapy Spider')
    parser.add_argument('--start_urls', required=True, help='Comma-separated list of start URLs for spider')
    parser.add_argument('--allowed_domains', required=True, help='Comma-separated list of allowed domains')
    parser.add_argument('--output_file', required=True, help='Output file to save results')
    args = parser.parse_args()

    start_urls = args.start_urls.split(',')
    allowed_domains = args.allowed_domains.split(',')
    print("start urls ===========",start_urls,allowed_domains)
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    })

    process.crawl(UrlCrawlSpider, start_urls=start_urls, allowed_domains=allowed_domains, output_file=args.output_file)
    process.start()

if __name__ == "__main__":
    main()