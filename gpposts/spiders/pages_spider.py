import scrapy
import logging
import locale, csv

locale.setlocale(locale.LC_ALL, 'de_CH.utf8') 

class PagesSpider(scrapy.Spider):
    name = 'pages'

    custom_settings = {
        'ROBOTSTXT_OBEY': 0,
        'FEED_URI': 'pages_de.xml',
        'FEED_FORMAT': 'xml',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def start_requests(self):
        # Get start urls from CSV file
        with open('pages-to-archive.csv') as csv_data:
            reader = csv.reader(csv_data)

            # eliminate blank rows if they exist
            rows = [row for row in reader if row]
            headings = rows[0] # get headings
            for row in rows:
                start_url = 'http://www.greenpeace.org' + row[0]
                logging.debug('Start URL: ' + start_url)
                try:
                    yield scrapy.Request(url=start_url, callback=self.parseType2)
                except:
                    pass

    def parseType1(self, response):

        yield {
            'type': 'Page',
            'language': 'de',
            'supertitle': response.css('div.article h1:first-child span::text').extract_first(),
            'title': response.css('div.article h2 span::text').extract_first(),
            'author': '',
            'date': response.css('div.article div.text span.author::text').re_first(r' - \s*(.*)'),
            #'lead': extract_with_css('div.news-list div.post-content *:first-child strong::text'),
            'lead': response.xpath("string(//div[contains(concat(' ', normalize-space(@class), ' '), ' article ')]/*/*/div[@class='leader'])").extract()[0],
            'categories': response.xpath('string(//div[@class="tags"][1]/ul)').extract()[0],
            'tags': response.xpath('string(//div[@class="tags"][2]/ul)').extract()[0],
            'text':  response.xpath('//div[@class="text"]/div[not(@id) and not(@class)]').extract_first(),
            'remove': response.css('div.img-view.galleria_container').extract_first(),
            'remove2': response.xpath('//span[@class="btn-open"]').extract_first(),
            'remove3': response.css('div.gallery div.navi').extract_first(),
            'imagesA': response.xpath('//div[@class="news-list"]//div[@class="post-content"]//a[img]/@href').extract(),
            #'imagesB': response.xpath('//div[@class="news-list"]//div[@class="post-content"]//img[not(ancestor::a)]/@src').extract(), #don't import image if there's an a tag around it
            'imagesB': response.xpath('//div[@class="news-list"]//div[@class="post-content"]//img/@src').extract(),
            'imagesC': response.xpath('//div[@class="gallery"]//div[@class="img-nav"]//a/@rel').extract(), # Galleries (horrible html)
            'pdfFiles': response.css('div.post-content a[href$=".pdf"]::attr(href)').extract(),
            'url': response.url,
        }

    def parseType2(self, response):

        yield {
            'type': 'Page',
            'language': 'de',
            'supertitle': '',
            'title': response.css('div.hub-text-above h1').extract(),
            'author': '',
            'date': '',
            #'lead': extract_with_css('div.news-list div.post-content *:first-child strong::text'),
            'lead': '',
            'categories': response.xpath('string(//div[@class="tags"][1]/ul)').extract()[0],
            'tags': response.xpath('string(//div[@class="tags"][2]/ul)').extract()[0],
            'text':  response.xpath('//div[@class="hub-text-above"]').extract_first(),
            'remove': response.css('div.img-view.galleria_container').extract_first(),
            'remove2': response.xpath('//span[@class="btn-open"]').extract_first(),
            'remove3': response.css('div.gallery div.navi').extract_first(),
            'imagesA': response.xpath('//div[@class="news-list"]//div[@class="post-content"]//a[img]/@href').extract(),
            #'imagesB': response.xpath('//div[@class="news-list"]//div[@class="post-content"]//img[not(ancestor::a)]/@src').extract(), #don't import image if there's an a tag around it
            'imagesB': response.xpath('//div[@class="news-list"]//div[@class="post-content"]//img/@src').extract(),
            'imagesC': response.xpath('//div[@class="gallery"]//div[@class="img-nav"]//a/@rel').extract(), # Galleries (horrible html)
            'pdfFiles': response.css('div.post-content a[href$=".pdf"]::attr(href)').extract(),
            'url': response.url,
        }
