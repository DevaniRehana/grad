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

url = 'https://www.googleapis.com/auth/bigquery'
PROJECT_NUMBER = '233574384747'
credentials = AppAssertionCredentials(scope=url)
httpss = credentials.authorize(httplib2.Http())
bigquery_service = build('bigquery','v2',http=httpss)

def filehandler(option):
    file_path = 'MyFiles/Consumer_Complaints10k.csv'
    fp = open(file_path,'r')
    alldata = csv.reader(fp,delimiter=',')
    rownum = 1
    dictState = {}
    dictyear = {}
    dictprod = {}
    dictsubpro = {}
    dictcomp = {}
    dictresp = {}
    dictStateYear = {}
    for row in alldata:
        count = 1
        if rownum == 1:
            rownum = 0
            continue
        row = ['NULL' if x=='' else x for x in row]
        state = row[5]
        try:
            year = row[8].split('/')[2]
        except:
            year = 1000
        product = row[1]
        subproduct = row[2]
        Company = row[10]
        response = row[11]
        '''rowdict = {'complaintid':row[0],'Product':row[1],'Subproduct':row[2],
                   'Issue':row[3],'Subissue':row[4],'State':row[5],
                   'ZIP_code':row[6],'Submitted_via':row[7],'Date_received':row[8],
               'Date_sent_to_company':row[9] ,'Company':row[10],'Company_response':row[11],
               'Timely_response':row[12] ,'Consumer_disputed':row[13]}'''
        if state in dictState:
            dictState[state] += count
        else:
            dictState[state] = count
        if year in dictyear:
            dictyear[year] += count
        else:
            dictyear[year] = count
        if product in dictprod:
            dictprod[product] += count
        else:
            dictprod[product] = count
        if subproduct in dictsubpro:
            dictsubpro[subproduct] += count
        else:
            dictsubpro[subproduct] = count
        if Company in dictcomp:
            dictcomp[Company] += count
        else:
            dictcomp[Company] = count
        if response in dictresp:
            dictresp[response] += count
        else:
            dictresp[response] = count
        key = state,year
        if key in dictStateYear:
            dictStateYear[key] += count
        else:
            dictStateYear[key] = count
    resp = []
    if option == '1':
        for company in dictcomp:
            resp.append({"count":dictcomp[company],"company":company})
    elif option == '2':
        for state in dictState:
            resp.append({"count":dictState[state],"state":state})
    elif option == '3':
        for company in dictcomp:
            resp.append({"count":dictcomp[company],"company":company})
    elif option == '4':
        for pro in dictprod:
            resp.append({"count":dictprod[pro],"product":pro})
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
        opt = '4'
        resp = filehandler(opt)
        temp_data = str(resp)
        temp_path = 'Templates/chart1.html'
        self.response.out.write(template.render(temp_path,{'temp_data':temp_data}))
        
class DisplayChart2(webapp2.RequestHandler):
    def get(self):
        opt = '2'
        resp = filehandler(opt)
        temp_data = str(resp)
        temp_path = 'Templates/chart2.html'
        self.response.out.write(template.render(temp_path,{'temp_data':temp_data}))

class DisplayChart3(webapp2.RequestHandler):
    def get(self):
        opt = '4'
        resp = filehandler(opt)
        temp_data = str(resp)
        temp_path = 'Templates/chart3.html'
        self.response.out.write(template.render(temp_path,{'temp_data':temp_data}))

class DisplayChart4(webapp2.RequestHandler):
    def get(self):
        opt = '3'
        resp = filehandler(opt)
        temp_data = str(resp)
        temp_path = 'Templates/chart4.html'
        self.response.out.write(template.render(temp_path,{'temp_data':temp_data}))
     
 
application = webapp2.WSGIApplication([
    ('/displayChart1',DisplayChart1),
    ('/displayChart2',DisplayChart2),
    ('/displayChart3',DisplayChart3),
    ('/displayChart4',DisplayChart4),
    ('/getChartData',GetChartData),
    ('/', ShowHome),
], debug=True)
