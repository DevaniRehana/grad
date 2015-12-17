# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 18:25:29 2015

@author: Harish_kamuju
"""
from twython import Twython, TwythonStreamer
import os, time

APP_KEY = '3GAWA2Rp0Mpqqb9xlrdPoVySA'
APP_SECRET = 'VkR3faQPNPj5qM0m0tbaB7Ms4vA5Lad9Nc1q5eev1EiwDfevQP'
ACCESS_TOKEN = '3277952539-Omnj5McBKa8GuVJaLImFNxgayUT86DyeQYXF5nd'
ACCESS_TOKEN_SECRET = '50MfEz02f5lN7pFl1skGPKxHa9AlJO9DsrNox2XD3hheO'

FILE_NAME = 'data/jeter'

class MyStreamer(TwythonStreamer):
    def on_success(self, data):
		savefile = open(FILE_NAME, 'a+')
		statinfo = os.stat(FILE_NAME)
		if statinfo.st_size < 1000000:
			try:
				print data['coordinates']['coordinates']
				print statinfo.st_size
				try:
					data['text'].encode('utf-8')
					savefile.write('username=:'+data['user']['name'] + '\n')
					savefile.write('screenname=:'+data['user']['screen_name'] + '\n')
					text = data['text'].encode('utf-8')
					finaltext = text.replace('\n', '\t')
					savefile.write('text=:'+finaltext + '\n')
					savefile.write('time=:' + data['created_at'] + '\n')
					savefile.write('longitude=:'+str(data['coordinates']['coordinates'][0]) + '\n')
					savefile.write('latitude=:'+str(data['coordinates']['coordinates'][1]) + '\n')
					savefile.write('\n')
					
					#print data['text']
				except:
					print 'text not encodable'
			except:
				print 'No coordinates'
		else:
			self.disconnect()
		savefile.close()

    def on_error(self, status_code, data):
        print status_code
        self.disconnect()


stream = MyStreamer(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
stream.statuses.filter(track='derek jeter', locations='-180,-90,180,90')
