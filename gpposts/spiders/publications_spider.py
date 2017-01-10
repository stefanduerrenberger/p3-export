import scrapy
import logging
import locale

locale.setlocale(locale.LC_ALL, 'fr_CH.utf8') 

class PublicationsSpider(scrapy.Spider):
    name = 'publications'

    custom_settings = {
        'ROBOTSTXT_OBEY': 0,
        #'DEPTH_LIMIT': 4,
        'FEED_URI': 'publications_de.xml',
        'FEED_FORMAT': 'xml',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def start_requests(self):
        start_urls = ['http://www.greenpeace.org/switzerland/de/?tab=4']

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
        

    def parse(self, response):
        # follow links to blog pages
        for href in response.css('div.news-content h3 a::attr(href)').extract():
            yield scrapy.Request(response.urljoin(href), callback=self.parse_publication)

        # follow pagination links
        url_part = response.css('a.next::attr("href")').extract_first()
        next_page = 'http://www.greenpeace.org/switzerland/de/' + url_part;
        
        logging.info("url_part: " + url_part)
        logging.info("Next page link: " + next_page)

        if url_part is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_publication(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first()

        yield {
            'type': 'Blog',
            'supertitle': extract_with_css('div.article h1 span::text'),
            'title': response.css('div.article h2 span::text').extract_first(),
            'author': '',
            'date': response.css('div.article div.text span.author::text').re_first(r' - \s*(.*)'),
            #'lead': response.css('div.article div.text div.leader').extract(),
            'lead': response.xpath("string(//div[contains(concat(' ', normalize-space(@class), ' '), ' article ')]/*/*/div[@class='leader'])").extract()[0],
            'categories': response.xpath('string(//div[@class="tags"][1]/ul)').extract()[0],
            'tags': response.xpath('string(//div[@class="tags"][2]/ul)').extract_first(),
            'text':  response.xpath('//div[@class="text"]/div[not(@id) and not(@class)]').extract_first(),
            'remove': response.css('div.img-view.galleria_container').extract_first(),
            'remove2': response.xpath('//span[@class="btn-open"]').extract_first(),
            'imagesA': response.xpath('//div[@class="text"]/div[not(@id) and not(@class)]//a[img]/@href').extract(),
            #'imagesB': response.xpath('//div[@class="text"]/div[not(@id) and not(@class)]//img[not(ancestor::a)]/@src').extract(), #don't import image if there's an a tag around it
            'imagesB': response.xpath('//div[@class="text"]/div[not(@id) and not(@class)]//img/@src').extract(),
            'imagesC': response.xpath('//div[@class="gallery"]//div[@class="img-nav"]//a/@rel').extract(), # Galleries (horrible html)
            'pdfFiles': response.css('div.article a[href$=".pdf"]::attr(href)').extract(),
            'url': response.url,
        }

class PublicationsFrSpider(scrapy.Spider):
    name = 'publications_fr'

    custom_settings = {
        'ROBOTSTXT_OBEY': 0,
        #'DEPTH_LIMIT': 4,
        'FEED_URI': 'publications_fr.xml',
        'FEED_FORMAT': 'xml',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def start_requests(self):
        start_urls = ['http://www.greenpeace.org/switzerland/fr/?tab=4']

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
        

    def parse(self, response):
        # follow links to blog pages
        for href in response.css('div.news-content h3 a::attr(href)').extract():
            yield scrapy.Request(response.urljoin(href), callback=self.parse_publication)

        # follow pagination links
        url_part = response.css('a.next::attr("href")').extract_first()
        next_page = 'http://www.greenpeace.org/switzerland/fr/' + url_part;
        
        logging.info("url_part: " + url_part)
        logging.info("Next page link: " + next_page)

        if url_part is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_publication(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first()

        yield {
            'type': 'Blog',
            'supertitle': extract_with_css('div.article h1 span::text'),
            'title': response.css('div.article h2 span::text').extract_first(),
            'author': '',
            'date': response.css('div.article div.text span.author::text').re_first(r' - \s*(.*)'),
            #'lead': response.css('div.article div.text div.leader').extract(),
            'lead': response.xpath("string(//div[contains(concat(' ', normalize-space(@class), ' '), ' article ')]/*/*/div[@class='leader'])").extract()[0],
            'categories': response.xpath('string(//div[@class="tags"][1]/ul)').extract()[0],
            'tags': response.xpath('string(//div[@class="tags"][2]/ul)').extract_first(),
            'text':  response.xpath('//div[@class="text"]/div[not(@id) and not(@class)]').extract_first(),
            'remove': response.css('div.img-view.galleria_container').extract_first(),
            'remove2': response.xpath('//span[@class="btn-open"]').extract_first(),
            'imagesA': response.xpath('//div[@class="text"]/div[not(@id) and not(@class)]//a[img]/@href').extract(),
            #'imagesB': response.xpath('//div[@class="text"]/div[not(@id) and not(@class)]//img[not(ancestor::a)]/@src').extract(), #don't import image if there's an a tag around it
            'imagesB': response.xpath('//div[@class="text"]/div[not(@id) and not(@class)]//img/@src').extract(),
            'imagesC': response.xpath('//div[@class="gallery"]//div[@class="img-nav"]//a/@rel').extract(), # Galleries (horrible html)
            'pdfFiles': response.css('div.article a[href$=".pdf"]::attr(href)').extract(),
            'url': response.url,
        }