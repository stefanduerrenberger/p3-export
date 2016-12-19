#!/usr/bin/python
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
from datetime import datetime
from scrapy.exceptions import DropItem
import locale

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
			date_object = datetime.strptime(item['date'], '%d. %B, %Y am %H:%M')
			item['date'] = date_object.strftime('%Y-%m-%d %H:%M')
		except Exception:
			try:
				date_object = datetime.strptime(item['date'], '%d. %B, %Y')
				item['date'] = date_object.strftime('%Y-%m-%d %H:%M')
			except Exception:
				pass

		# text remove unwanted strings
		try:
			text = item['text']
			remove = item['remove']
			text = text.replace(remove, '')

			item['text'] = text
		except Exception:
			pass

		#logging.debug('trying to grab images from text')
		#logging.debug("Text: " + item['text'])
		#item['images'] = 'test'
		return item
