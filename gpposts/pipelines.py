#!/usr/bin/python
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
from datetime import datetime
from scrapy.exceptions import DropItem
import locale, re

locale.setlocale(locale.LC_ALL, 'de_CH.utf8') 

class GppostsPipeline(object):
	def __init__(self):
		self.titles_seen = set()

	def process_item(self, item, spider):
		# Duplicate filter
		if item['title'] in self.titles_seen:
			raise DropItem("Duplicate item found: %s" % item)
		else:
			self.titles_seen.add(item['title'])

		# Date format
		try:
			date_object = datetime.strptime(item['date'].encode("utf8"), '%d. %B, %Y am %H:%M')
			item['date'] = date_object.strftime('%Y-%m-%d %H:%M')
		except Exception:
			try:
				date_object = datetime.strptime(item['date'].encode("utf8"), '%d. %B, %Y')
				item['date'] = date_object.strftime('%Y-%m-%d %H:%M')
			except Exception:
				logging.exception('Date conversion exception')
				pass

		# text remove unwanted strings
		try:
			# remove unwanted strings already found by crawler
			text = item['text']

			# Image gallery title image
			remove = item['remove']
			text = text.replace(remove, '')
			
			# remove open button in gallery (might be included in the title image code)
			remove2 = item['remove2']
			text = text.replace(remove2, '')

			# convert h1 to h2
			text = text.replace('<h1>', '<h2>')
			text = text.replace('</h1>', '</h2>')
			text = text.replace('&lt;h1&gt;', '&lt;h2&gt;')
			text = text.replace('&lt;/h1&gt;', '&lt;/h2&gt;')

			item['text'] = text
		except Exception:
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

		#logging.debug('trying to grab images from text')
		#logging.debug("Text: " + item['text'])
		#item['images'] = 'test'
		return item
