#!/usr/bin/python
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
from datetime import datetime
from scrapy.exceptions import DropItem
import locale, re, csv

locale.setlocale(locale.LC_ALL, 'de_CH.utf8') 

class GppostsPipeline(object):
    def __init__(self):
        self.titles_seen = set()

    def process_item(self, item, spider):
        # sort out the titles, the french version has multiple ways of using titles that we get in either the supertitle or title:
        if ('supertitle' in item) and item['supertitle']:
            if item['title']:
                supertitle = item['supertitle']
                
                if supertitle[-1] == ':': # Some Supertitles already have a :
                    item['title'] = item['supertitle'] + ' ' + item['title']
                else:
                    item['title'] = item['supertitle'] + ': ' + item['title']
            else:
                item['title'] = item['supertitle']

        # Duplicate filter by title
        if item['title'] in self.titles_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.titles_seen.add(item['title'])

        # Date format
        if item['date']:
            try:
                date_object = datetime.strptime(item['date'].encode("utf8"), '%d. %B, %Y am %H:%M')
                item['date'] = date_object.strftime('%Y-%m-%d %H:%M')
            except Exception:
                try:
                    date_object = datetime.strptime(item['date'].encode("utf8"), '%Y-%B-%d %H:%M')
                    item['date'] = date_object.strftime('%Y-%m-%d %H:%M')
                except Exception:
                    try:
                        date_object = datetime.strptime(item['date'].encode("utf8"), '%d. %B, %Y')
                        item['date'] = date_object.strftime('%Y-%m-%d %H:%M')
                    except Exception:
                        try:
                            date_object = datetime.strptime(item['date'].encode("utf8"), '%d %B, %Y à %H:%M')
                            item['date'] = date_object.strftime('%Y-%m-%d %H:%M')
                        except Exception:
                            try:
                                date_object = datetime.strptime(item['date'].encode("utf8"), '%d %B, %Y')
                                item['date'] = date_object.strftime('%Y-%m-%d %H:%M')
                            except Exception:
                                logging.exception('Date conversion exception:' + item['date'])
                                pass

        # text remove unwanted strings
        try:
            # remove unwanted strings already found by crawler
            text = item['text']

            if text:
                # Remove image gallery title image
                remove = item['remove']
                if remove:
                    text = text.replace(remove, '')
                
                # Remove open button in gallery (might be included in the title image code)
                remove2 = item['remove2']
                if remove2:
                    text = text.replace(remove2, '')

                # Remove gallery navigation
                if item['remove3']:
                    text = text.replace(item['remove3'], '')

                # convert h1 to h2
                text = text.replace('<h1>', '<h2>')
                text = text.replace('</h1>', '</h2>')
                text = text.replace('&lt;h1&gt;', '&lt;h2&gt;')
                text = text.replace('&lt;/h1&gt;', '&lt;/h2&gt;')

                # convert http to https in youtube links
                text = text.replace('http://www.youtube.com', 'https://www.youtube.com')

                item['text'] = text
        except Exception:
            logging.exception('Text conversion exception')
            pass

        # Gallery images (imagesC)
        try:
            images = item['imagesC']
            
            for i, image in enumerate(images):
                logging.debug('Gallery Image: ' + image)
                image = re.sub('^(.*)\~\^\/switzerland\/', 'http://www.greenpeace.org/switzerland/', image)
                image = re.sub('\~\^[0-9]*$', '', image)
                logging.debug('Gallery Image Converted: ' + image)
                images[i] = image

            #logging.debug('All gallery images: ' + join(str(p) for p in images) )

            item['imagesC'] = images
        except Exception:
            logging.exception('Gallery image conversion')
            pass

        # Categories and tags conversion (into tags)
        item['oldCategories'] = item['categories']
        item['oldTags'] = item['tags']
        newTags = set()

        # Convert categories, but save them into tags
        if item['categories']:
            # convert tags string to list
            itemTagsString = item['categories']

            itemTags = itemTagsString.split(",")

            with open('category-conversion.csv') as csv_data:
                reader = csv.reader(csv_data)

                # eliminate blank rows if they exist
                rows = [row for row in reader if row]
                headings = rows[0] # get headings
                conversionDictionary = {};
                for row in rows:
                    conversionDictionary[row[0].lower()] = row[1]


            # convert the tags, but only save them once if they are converted to the same new tag
            for tag in itemTags:
                tag = tag.strip().lower()
                if tag in conversionDictionary:
                    logging.debug('Categories: replacing ' + tag + ' with ' + conversionDictionary[tag])

                    if tag not in newTags:
                        convertedTag = conversionDictionary[tag]

                        # convertedTag
                        newTags.add(convertedTag)
                else:
                    logging.info('Not in tag conversion list: ' + tag)


        # Tags conversion
        if item['tags']:
            # convert tags string to list
            itemTagsString = item['tags']
            #logging.debug('Tags string: ' + itemTagsString )
            itemTags = itemTagsString.split(",")
            #logging.debug('Tags list: ' + str(itemTags) )

            with open('category-conversion.csv') as csv_data:
                reader = csv.reader(csv_data)

                # eliminate blank rows if they exist
                rows = [row for row in reader if row]
                headings = rows[0] # get headings
                conversionDictionary = {};
                for row in rows:
                    conversionDictionary[row[0].lower()] = row[1]


            # convert the tags, but only save them once if they are converted to the same new tag
            for tag in itemTags:
                tag = tag.strip().lower()
                if tag in conversionDictionary:
                    logging.debug('Tags: replacing ' + tag + ' with ' + conversionDictionary[tag])

                    if tag not in newTags:
                        convertedTag = conversionDictionary[tag]

                        # convertedTag
                        newTags.add(convertedTag)
                else:
                    logging.info('Not in tag conversion list: ' + tag)

        logging.debug('Converted Tags: ' + str(newTags))

        # save the tags back to item['tags']
        item['tags'] = ",".join(newTags) 

        # get the slug from the URL
        try:
            if item['type'] in ('Blog', 'Story'):
                if item['language'] == 'de':
                    found = re.findall('^http:\/\/www.greenpeace.org(.*)\/(.*)\/blog\/([0-9]*)\/$', item['url'])
                    item['slug'] = found[0][1].strip()
                elif item['language'] == 'fr':
                    item['slug'] = '' # Doesn't have a slug in the URL

            elif item['type'] == 'PressRelease':
                if item['language'] == 'de':
                    found = re.findall('^http:\/\/www.greenpeace.org(.*)\/Medienmitteilungen\/(.*)\/$', item['url'])
                    item['slug'] = found[0][1].strip()
                elif item['language'] == 'fr':
                    found = re.findall('^http:\/\/www.greenpeace.org(.*)\/communiques\/(.*)\/(.*)\/$', item['url'])
                    item['slug'] = found[0][2].strip()

            elif item['type'] == 'Publication':
                if item['language'] == 'de':
                    found = re.findall('^http:\/\/www.greenpeace.org(.*)\/Publikationen\/([a-zA-Z-]*)\/(.*)\/$', item['url'])
                    item['slug'] = found[0][2].strip()
                elif item['language'] == 'fr':
                    found = re.findall('^http:\/\/www.greenpeace.org(.*)\/publications\/documents\/(.*)\/$', item['url'])
                    item['slug'] = found[0][1].strip()
        except Exception:
            logging.info('Failed to find slug:' + item['date'])
            pass

        # Finished, return the item
        return item
