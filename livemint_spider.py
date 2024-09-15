import scrapy
from scrapy.crawler import CrawlerProcess

class LivemintSpider(scrapy.Spider):
    name = "livemint"
    allowed_domains = ["economictimes.indiatimes.com"]
    start_urls = ['https://economictimes.indiatimes.com']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 5,
        'DOWNLOAD_DELAY': 2,
        'FEEDS': {
            'output/livemint_articles.json': {
                'format': 'json',
                'encoding': 'utf8',
                'indent': 4,  # Format the JSON with indentation for readability
            }
        }
    }

    def parse(self, response):
        # Extract article links from the homepage
        for href in response.xpath('//a[contains(@href, "news")]/@href').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        # Extract required fields from the article page
        article_url = response.url
        title = response.xpath('//h1/text()').get().strip()

        # Extract author names and URLs
        authors = response.xpath('//span[@class="premiumarticleInfo premiumauthor"]/a')
        author_list = []
        for author in authors:
            author_name = author.xpath('text()').get().strip()
            author_url = response.urljoin(author.xpath('@href').get().strip())
            author_list.append({'Author Name': author_name, 'Author URL': author_url})

        # Extract article content
        content = ' '.join(response.xpath('//p/text()').getall()).strip()

        # Extract the published date
        published_date = response.xpath('//meta[@property="article:published_time"]/@content').get()

        # Store the extracted data in JSON format
        yield {
            'Article URL': article_url,
            'Title': title,
            'Authors': author_list,  # List of authors and their URLs
            'Article Content': content,
            'Published Date': published_date,
        }

