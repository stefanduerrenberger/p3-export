import scrapy
import logging
import locale

locale.setlocale(locale.LC_ALL, 'de_CH.utf8') 

class BlogsFrSpider(scrapy.Spider):
    name = 'blogs_fr'

    def start_requests(self):
        start_urls = ['http://www.greenpeace.org/switzerland/fr/publications/actualites/?page=1']

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
        

    def parse(self, response):
        # follow links to blog pages
        for href in response.css('div.news-content h3 a::attr(href)').extract():
            if ("Newsblog" in href) or ("Kunos-Kolumne" in href) or ("blog" in href):
                yield scrapy.Request(response.urljoin(href), callback=self.parse_blog)
            else:
                yield scrapy.Request(response.urljoin(href), callback=self.parse_story)

        # follow pagination links
        url_part = response.css('a.next::attr("href")').extract_first()
        next_page = 'http://www.greenpeace.org/switzerland/fr/publications/actualites/' + url_part;
        
        logging.info("url_part: " + url_part)
        logging.info("Next page link: " + next_page)

        if url_part is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_blog(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first()

        yield {
            'type': 'Blog',
            'title': extract_with_css('div.news-list h1::text'),
            'author': response.xpath('string(//div[@class="news-list"]/ul/li/*/*/span[@class="caption"]/span[@class="green1"]/strong)').re_first(r'von \s*(.*)'),
            'date': response.css('div.news-list .caption::text').re_first(r' - \s*(.*)'),
            #'lead': extract_with_css('div.news-list div.post-content *:first-child strong::text'),
            'lead': response.xpath('string(//div[@class="news-list"]/ul/li/div[@class="post-content"]/div//*[self::p or self::h3 or self::h2][1])').extract()[0],
            'categories': response.xpath('string(//div[@class="tagsandtopics"]/div[@class="tags"][1]/ul)').extract()[0],
            'tags': response.xpath('string(//div[@class="tagsandtopics"]/div[@class="tags"][2]/ul)').extract()[0],
            'text':  response.css('div.news-list div.post-content').extract_first(),
            'remove': response.css('div.img-view.galleria_container').extract_first(),
            'remove2': response.xpath('//span[@class="btn-open"]').extract_first(),
            'imagesA': response.xpath('//div[@class="news-list"]//div[@class="post-content"]//a[img]/@href').extract(),
            #'imagesB': response.xpath('//div[@class="news-list"]//div[@class="post-content"]//img[not(ancestor::a)]/@src').extract(), #don't import image if there's an a tag around it
            'imagesB': response.xpath('//div[@class="news-list"]//div[@class="post-content"]//img/@src').extract(),
            'imagesC': response.xpath('//div[@class="gallery"]//div[@class="img-nav"]//a/@rel').extract(), # Galleries (horrible html)
            'pdfFiles': response.css('div.post-content a[href$=".pdf"]::attr(href)').extract(),
            'url': response.url,

            #'imagesB': response.xpath('//div[@class="news-list"]//div[@class="post-content"]//img/@src'),
        }

    def parse_story(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first()

        yield {
            'type': 'Story',
            'supertitle': extract_with_css('div.article h1 span::text'),
            'title': extract_with_css('div.article h2 span::text'),
            'author': '',
            'date': response.css('div.article div.text span.author::text').re_first(r' - \s*(.*)'),
            #'lead': response.css('div.article div.text div.leader').extract(),
            'lead': response.xpath("string(//div[contains(concat(' ', normalize-space(@class), ' '), ' article ')]/*/*/div[@class='leader'])").extract()[0],
            'categories': response.xpath('string(//div[@class="tagsandtopics"]/div[@class="tags"][1]/ul)').extract()[0],
            'tags': response.xpath('string(//div[@class="tagsandtopics"]/div[@class="tags"][2]/ul)').extract_first(),
            'text':  response.xpath('//div[@class="text"]/div[not(@id) and not(@class)]').extract_first(),
            'remove': response.css('div.img-view.galleria_container').extract_first(),
            'remove2': response.xpath('//span[@class="btn-open"]').extract_first(),
            'imagesA': response.xpath('//div[@class="text"]/div[not(@id) and not(@class)]//a[img]/@href').extract(),
            #'imagesB': response.xpath('//div[@class="text"]/div[not(@id) and not(@class)]//img[not(ancestor::a)]/@src').extract(), #don't import image if there's an a tag around it
            'imagesB': response.xpath('//div[@class="text"]/div[not(@id) and not(@class)]//img/@src').extract(),
            'imagesC': response.xpath('//div[@class="gallery"]//div[@class="img-nav"]//a/@rel').extract(), # Galleries (horrible html)
            'pdfFiles': response.css('div.post-content a[href$=".pdf"]::attr(href)').extract(),
            'url': response.url,
            'subtitle': extract_with_css('div.article h2 span::text'),
        }