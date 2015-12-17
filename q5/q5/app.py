# -*- coding: utf-8 -*-
"""
Created on Mon Jul 06 18:25:29 2015

@author: Harish_kamuju
"""

import httplib2
import webapp2
from google.appengine.ext.webapp import template
from apiclient.discovery import build
from oauth2client.appengine import AppAssertionCredentials
import json
import numpy as np
import csv





def filehandler(option):
    file_path = 'MyFiles/harishkamuju.csv'
    fp = open(file_path,'r')
    alldata = csv.reader(fp,delimiter=',')
    
    rownum = 1
    dictsa = {}
    dictsd = {}
    dictad = {}
    #survived = row[1], sex = row[3],age=row[4],dest= row[13]
    for row in alldata:
        if rownum == 1:
            rownum = 0
            continue
        row = ['NULL' if x=='' else x for x in row]
        survived = row[1]
        sex = row[3]
        age=row[4]
        dest= row[13]
        key = sex,age
        key2 = sex,dest
        key3 = age,dest
        
        #Calculated the number of survivors based on the user provided columns
        if key in dictsa:
            dictsa[key] += int(survived)
        else:
            dictsa[key] = int(survived)
        if key2 in dictsd:
            dictsd[key2] += int(survived)
        else:
            dictsd[key2] = int(survived)
        
        if key3 in dictad:
            dictad[key3] += int(survived)
        else:
            dictad[key3] = int(survived)
    
    resp = []
    if option in ['1']:
        for key in dictsa:
            resp.append({"Survivedcount":dictsa[key],"SexAge":str(key)})
            
    elif option == '2':
        for key in dictsd:
            resp.append({"Survivedcount":dictsd[key],"SexDest":str(key)})
    elif option == '3':
        for key in dictad:
            resp.append({"Survivedcount":dictad[key],"AgeDest":str(key)})
    return resp
        
class ShowHome(webapp2.RequestHandler):
    def get(self):
        template_data = {}
        template_path = 'Templates/index.html'
        self.response.out.write(template.render(template_path,{'template_data':template_data}))
        


class GetChartData(webapp2.RequestHandler):
  def get(self):
    inputData = self.request.get("inputData")
    resp = []
    
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(resp))

class DisplayChart1(webapp2.RequestHandler):
    def get(self):
        opt = '1'
        resp = filehandler(opt)
        temp_data = str(resp)
        temp_path = 'Templates/chart1.html'
        self.response.out.write(template.render(temp_path,{'temp_data':temp_data,'value':opt}))
        
class DisplayChart2(webapp2.RequestHandler):
    def get(self):
        opt = '2'
        resp = filehandler(opt)
        temp_data = str(resp)
        temp_path = 'Templates/chart1.html'
        self.response.out.write(template.render(temp_path,{'temp_data':temp_data,'value':opt}))

class DisplayChart3(webapp2.RequestHandler):
    def get(self):
        opt = '3'
        resp = filehandler(opt)
        temp_data = str(resp)
        temp_path = 'Templates/chart1.html'
        self.response.out.write(template.render(temp_path,{'temp_data':temp_data,'value':opt}))

class DisplayChart4(webapp2.RequestHandler):
    def get(self):
        opt = '4'
        resp = filehandler(opt)
        temp_data = str(resp)
        temp_path = 'Templates/chart1.html'
        self.response.out.write(template.render(temp_path,{'temp_data':temp_data,'value':opt}))
        
class DisplayChart5(webapp2.RequestHandler):
    def get(self):
        inputData = self.request.get("inputData")
        temp_data = str(inputData)
        temp_path = 'Templates/chart1.html'
        self.response.out.write(template.render(temp_path,{'temp_data':temp_data,'value':'none'}))
 
application = webapp2.WSGIApplication([
    ('/displayChart1',DisplayChart1),
    ('/displayChart2',DisplayChart2),
    ('/displayChart3',DisplayChart3),
    ('/displayChart4',DisplayChart4),
    ('/displayChart5',DisplayChart5),
    ('/getChartData',GetChartData),
    ('/', ShowHome),
], debug=True)
