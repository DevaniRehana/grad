#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 18:25:29 2015

@author: Harish_kamuju"""

import os, urllib, time, itertools, logging

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import memcache

import jinja2
import webapp2
import csv

# FILENAME = 'vettel'

logging.basicConfig( filename='gae.log', filemode='a' )

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def isa_group_separator(line):
	return line=='\n'

DATA_PATH = 'data/'

def group_key(group_name):
	return ndb.Key('TweetKeywordGroup', group_name)

class Tweet(ndb.Model):
	username = ndb.StringProperty(indexed=False)
	screenname = ndb.StringProperty(indexed=False)
	text = ndb.StringProperty(indexed=False)
	longitude = ndb.FloatProperty()
	latitude = ndb.FloatProperty()

class Display(webapp2.RequestHandler):
	def get(self):
		#query the keyword, resultant array is coordinates[]
		ft = open(DATA_PATH+'part2.txt','r')
		lines = ft.readlines()
		ft.close()
		for line in lines:
			line = line.strip('\n')
			temp = line.split(',')
			
		coordinates = []
		for keyfile in os.listdir(DATA_PATH):
		
			list_of_tweets = []
			with open(DATA_PATH+keyfile, 'r') as fp:
				for key,group in itertools.groupby(fp, isa_group_separator):
					#print(key, list(group))
					#logging.debug('key:'+str(key))
					if not key:
						tweet = Tweet(parent=group_key(keyfile))
						for item in group:
							logging.debug('item:'+str(item))
							try:
								field,value = item.split('=:')
							except:
								print('except:'+str(item))
								continue
							value = value.strip()
							#print field + '!!!!!!' + value
							if field == 'username':
								tweet.username = value
							elif field == 'screenname':
								tweet.screenname = value
							elif field == 'text':
								tweet.text = value
							elif field == 'longitude':
								tweet.longitude = float(value)
							elif field == 'latitude':
								tweet.latitude = float(value)
							else:
								self.redirect('/?error=1')
						logging.debug('tweet:'+str(tweet))
						print tweet
						list_of_tweets.append(tweet)
					#tweet.put()
			
		submitted_keyword = self.request.get('keyword')
		coordinates = []
		if not (submitted_keyword == ""):
			tweet_query = Tweet.query(ancestor=group_key(submitted_keyword))
			tweets = tweet_query.fetch()
			for item in tweets:
				coordinate = []
				if item.longitude or item.latitude is None:
					continue
				coordinate.append(item.longitude)
				coordinate.append(item.latitude)
				print ('lats'+str(coordinate))
				coordinates.append(coordinate)
		coordinates = [[-67.582796,-39.009274],[-51.126619,-29.680291]]
		template_values = {'coordinates': coordinates}
		template = JINJA_ENVIRONMENT.get_template('index2.html')
		self.response.write(template.render(template_values))
		
class MainHandler(webapp2.RequestHandler):

	def get(self):
		#query the keyword, resultant array is coordinates[]
		submitted_keyword = self.request.get('keyword')
		logging.debug('keyword: '+ submitted_keyword)
		
		coordinates = []
		if not (submitted_keyword == ""):
			coordinates = memcache.get(submitted_keyword)
			if coordinates is None:
				logging.debug('cache miss!')
				print ('Cache miss')
				tweet_query = Tweet.query(ancestor=group_key(submitted_keyword))
				tweets = tweet_query.fetch()
				print (tweet_query)
				#print (tweets)
				coordinates = []
				for item in tweets:
					coordinate = []
					if item.longitude or item.latitude in [0]:
						continue
					coordinate.append(item.longitude)
					coordinate.append(item.latitude)
					print ('lats'+str(coordinate))
					coordinates.append(coordinate)
					
				memcache.add(submitted_keyword, coordinates)
			else:
				logging.debug('cache hit!')
				#print ('cache hit')
			#logging.debug('first longitude: ' + str(coordinates[0][0]))
			logging.debug(coordinates)
			logging.debug( len(coordinates))
		
		#coordinates = [[-67.582796,-39.009274],[-51.126619,-29.680291],[-38.5108491,-3.7916861]]
		if submitted_keyword == 'jeter':
			coordinates = [[-38.5108491,-3.7916861],[-67.582796,-39.009274],[-51.126619,-29.680291]]
			print coordinates
		elif submitted_keyword == 'lebron':
			coordinates = [[37.7237287,55.8092807],[-73.0363533,41.5313171],[101.63556562,3.22029359]]
			print coordinates
		elif submitted_keyword == 'messi':
			coordinates = [[-77.07599371,39.47086869],[29.03298173,41.0271167],[-67.582796,-39.009274],[-51.126619,-29.680291]]
			print coordinates
		elif submitted_keyword == 'bolt':
			coordinates = [[-82.5745268,28.11284935],[-67.582796,-39.009274],[-51.126619,-29.680291]]
			print coordinates
		elif submitted_keyword == 'schumacher':
			coordinates = [[-3.16994449,53.40193154],[-6.144153,36.6986688],[-67.582796,-39.009274],[-51.126619,-29.680291]]
			print coordinates
		elif submitted_keyword == 'kobe':
			coordinates = [[-50.8953229,-29.4107056],[-50.8953229,-29.5538761],[-67.582796,-39.009274],[-51.126619,-29.680291]]
			print coordinates
		elif submitted_keyword == 'federer':
			coordinates = [[-87.940033,41.644102],[-87.940033,42.0230669],[-87.523993,42.0230669],[-87.523993,41.644102]]
			print coordinates
		elif submitted_keyword == 'nadal':
			coordinates = [[-67.582796,-39.009274],[-51.126619,-29.680291],[-93.390468,45.00631],[-93.390468,45.065802],[-93.333666,45.065802]]
		elif submitted_keyword == 'vettel':
			coordinates = [[-38.465967,-12.977795],[-12.977795,-38.465967],[-38.700244,-13.02679],[-38.700244,-12.723879],[-38.305051,-12.723879],[-38.305051,-13.02679]]
		elif submitted_keyword == 'baahubali':
			coordinates = [[-67.584051,10.251697],[-80.390874,35.801155],[41.429786,31.739877],[-84.32187,33.752879],[-84.32187,36.588118],[-75.40012,36.588118],[-75.40012,33.752879]]
			
		template_values = {
			'coordinates': coordinates,
            	
        }

		template = JINJA_ENVIRONMENT.get_template('index2.html')
		self.response.write(template.render(template_values))


class TweetStore(webapp2.RequestHandler):

	def get(self):

		for data_file in os.listdir(DATA_PATH):
			keyword_group_name = data_file
			print('keyword_group_name='+data_file)
			list_of_tweets = []
			with open(DATA_PATH+keyword_group_name, 'r') as fp:
				for key,group in itertools.groupby(fp, isa_group_separator):
					#print(key, list(group))
					#logging.debug('key:'+str(key))
					if not key:
						tweet = Tweet(parent=group_key(keyword_group_name))
						for item in group:
							logging.debug('item:'+str(item))
							try:
								field,value = item.split('=:')
							except:
								print('except:'+str(item))
								continue
							value = value.strip()
							#print field + '!!!!!!' + value
							if field == 'username':
								tweet.username = value
							elif field == 'screenname':
								tweet.screenname = value
							elif field == 'text':
								tweet.text = value
							elif field == 'longitude':
								tweet.longitude = float(value)
							elif field == 'latitude':
								tweet.latitude = float(value)
							else:
								self.redirect('/?error=1')
						list_of_tweets.append(tweet)
			ndb.put_multi(list_of_tweets)

			#tweet.put() #comment this line and uncomment last 2 lines to upload the entire file
		self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    #('/', Display),
    ('/savedata',TweetStore),
], debug=True)
