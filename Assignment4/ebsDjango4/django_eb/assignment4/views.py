# -*- coding: utf-8 -*-
"""
#Author Harish Kamuju
#UTA ID : 1001120930
#Section : 003 (6:00PM to 8:00PM)
#Assignment : 4
Created on Sat Jun 20 03:55:27 2015

"""
# Import the SDK

import boto
from boto.s3.key import Key
import os,datetime
import csv
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from random import randint

from boto import dynamodb2
from boto.dynamodb2.table import Table
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
#from elasticache_pyclient import MemcacheClient
#import memcache

#mc = memcache.Client(['a4cache.5odawy.cfg.usw2.cache.amazonaws.com:11211'],debug=1)

# Instantiate a new client for Amazon Simple Storage Service (S3). With no
# parameters or configuration, the AWS SDK for Python (Boto) will look for
# access keys in these environment variables:
#
access_key='AKIAINOHI7FXQD6PMNPA'
secret_key='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'
#
# For more information about this interface to Amazon S3, see:
# http://boto.readthedocs.org/en/latest/s3_tut.html

s3conn = boto.connect_s3(aws_access_key_id = access_key,
                     aws_secret_access_key = secret_key)

response = HttpResponse()
# Everything uploaded to Amazon S3 must belong to a bucket. These buckets are
# in the global namespace, and must have a unique name.
#
# For more information about bucket name restrictions, see:
# http://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html
mybucket = "kamuju"
#response.write ("<br>Using bucket : " + str(mybucket))
buck = s3conn.get_bucket(mybucket)
#memc = memcache.Client(['127.0.0.1:11211'], debug=1)

#bucket = s3.create_bucket(bucket_name)
   
#creates a random number of n digits given n.
def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

#Downloads files from bucket given the filename which acts as key.   
def downloadfiles():
    filename = raw_input("Enter the filename to dump data into Database:\n")
    if buck.get_key(filename):
        fkey = createkey(filename)
        fkey.get_contents_to_filename(filename)
        return filename
    else:
        response.write( "<br>No file in the bucket.Exiting!!")
        return response
        #sys.exit(0)
#Connects to RDS of AWS        
def connecttosql():
    try:    
        mydb = MySQLdb.connect(host = "awsdb.cppwhxblopbz.us-west-2.rds.amazonaws.com",
                     user="kamuju",passwd="password", port=3306, db="govdata")
        if mydb == None:
            response.write( '<br> Unable to connect to DataBase.Please try again later!Exiting')
            #sys.exit(0)
        else:
            return mydb
    except Exception as e:
        response.write( '<br>'+str(e.message)+'<br>')
        response.write( str(e.args))
        return response
        
#Inserts tables into RDS    
def insertdata(fp,filename,newkey):
    dbtime = ''
    mydb = connecttosql()
    cur = mydb.cursor()
    tablename = filename.split('.')[0]
    tablename = 'Consumer_Complaints60'
    cur.execute("show tables like '"+tablename+"'")
    row = cur.fetchone()
    #Creates table
    if not row:
        createtable = '''CREATE TABLE '''+tablename+''' (Complaint_ID int(11) NOT NULL,
        Product varchar(25) DEFAULT NULL,
        Subproduct varchar(45) DEFAULT NULL,
        Issue varchar(45) DEFAULT NULL,
        Subissue varchar(45) DEFAULT NULL,
        State varchar(5) DEFAULT NULL,
        ZIP_code int(11) DEFAULT NULL,
        Submitted_via varchar(12) DEFAULT NULL,
        Date_received datetime DEFAULT NULL,
        Date_sent_to_company datetime DEFAULT NULL,
        Company varchar(45) DEFAULT NULL,
        Company_response varchar(45) DEFAULT NULL,
        Timely_response varchar(5) DEFAULT NULL,
        Consumer_disputed varchar(5) DEFAULT NULL,
        PRIMARY KEY (Complaint_ID))'''
        
        cur.execute(createtable)
        mydb.commit()
    rows = cur.execute('select * from '+tablename)
    #Inserts records into the database.
    if rows == 0:
        add_row= '''INSERT INTO '''+tablename+'''(Complaint_ID,
                      Product ,
                      Subproduct,
                      Issue ,
                      Subissue ,
                      State ,
                      ZIP_code ,
                      Submitted_via ,
                      Date_received ,
                      Date_sent_to_company ,
                      Company ,
                      Company_response ,
                      Timely_response ,
                      Consumer_disputed) values (%s,'%s', '%s', "%s", '%s', '%s',%s,'%s', %s, %s, '%s','%s','%s','%s')
                     '''
        rownum = 1
        
        newkey.get_contents_to_filename('myfile.csv')
        ft = open('myfile.csv','r')
        alldata = csv.reader(ft,delimiter=',')
        
        st = datetime.datetime.now()
        for row in alldata:
            if rownum == 1:
                rownum = 0
                continue
            row = ['NULL' if x=='' else x for x in row]
            temp = add_row%tuple(row)
            try:
                cur.execute(temp)
                mydb.commit()
            except Exception as e:
                response.write( ('<br>DB Error!!'))
                response.write( '<br>'+str(e.message))
                response.write( '<br>'+str(e.args))
                continue
        et = datetime.datetime.now()
        dbtime = str(et-st)
    mydb.close()
    return dbtime,tablename


#Generates random queries 
def randomqueries(tablename):
    mydb = connecttosql()
    cur = mydb.cursor()
    repeats = [1000,5000,20000]
    for rep in repeats:
        count = 0
        start = datetime.datetime.now()
        while count < rep:
            count +=1
            randzip = randint(10000,99999)#random_with_N_digits(7)
            #response.write( count,randzip
            qry = "select Product,Issue,ZIP_code from "+tablename+" where ZIP_code="+str(randzip)
            #qry = "select zip_code from "+tablename+" where complaint_id="+str(randzip)
            cur.execute(qry)
            
        end = datetime.datetime.now()
        response.write( "<br>Time taken for "+str(rep)+" is :"+str(end-start))
    mydb.close()


#Creates a view of random tuples b/w 200-800 and generates 1k,5k,20k random search queries.
def r2queries(tablename):
    mydb = connecttosql()
    cur = mydb.cursor()
    repeats = [1000,5000,20000]
    randtuple = randint(200,800)
    newtable = 'ltd'+str(randtuple)
    temp = 'create view '+newtable+' as (select * from '+tablename+' limit '+str(randtuple)+')'
    cur.execute(temp)
    for rep in repeats:
        count = 0
        
        mydb.commit()
        start = datetime.datetime.now()
        while count < rep:
            count +=1
            randzip = randint(10000,99999)
            #response.write( count,randzip
            qry = "select Product,Issue,ZIP_code from "+newtable+" where ZIP_code="+str(randzip)
            #qry = "select zip_code from "+tablename+" where complaint_id="+str(randzip)
            cur.execute(qry)
            
        end = datetime.datetime.now()
        response.write( "<br>Time taken for limited "+str(randtuple)+"tuples "+str(rep)+" is :"+str(end-start))
    mydb.close()        

#Creates key for the filename         
def createkey(filename):
    newkey = Key(buck)
    newkey.key = filename
    return newkey
#Lists all the buckets in the s3
def listbuckets():
    response.write( "<br>List of buckets:")
    for bucket in s3conn.get_all_buckets():
        response.write( str(bucket)+'<br>')
    
def Mainpage(request):
    response.write('''<html><body><div align='center'><h1>Results Page
                    </h1><br>''')
    '''<form method="post">
              <p>Magnitude: <input type="number" name="mag" value=0 />.
              <input type="number" name="decimal" value=0 min="0" max="99"></p>
              <p>Location: <input type="text" name="loc" value ="" /></p>
              <p><input type="submit" /></p>'''
    
    tablename = request.GET.get('tablename')
    tname = tablename.split('.')[0]
    response.write('<h3>With Amazons Elastic cache</h3>')
    #response.write('<h3>With Amazons Elastic cache</h3>')
    #randomqueries(tname)
    r2queries(tname)
    #if request.method == 'POST':
     #   mag = request.get("mag")
      #  deci = request.get("decimal")
       # location = request.get("loc")
        #response.write('Mag:'+str(mag)+'Deci:'+str(deci)+'Loc:'+str(location))
    response.write('''</div></body></html>''')
    return response

def Upload(request):
    if request.method =='POST':
        filename = request.FILES['myfile'].name
        newkey = createkey(filename)
        start = datetime.datetime.now()
        newkey.set_contents_from_file(request.FILES['myfile'].file)
        fp = request.FILES['myfile'].file
        dbtime,tablename = insertdata(fp,filename,newkey)
        end = datetime.datetime.now()
        uptime = str(end-start)
        return render(request, 'upresult.html',{'time':uptime,'filename':filename,'dbtime':dbtime})
    else:        
        return render(request, 'name.html',{})

    
def Homepage(request):
    temp = '''<html><body><div align='center'><h1> AWS EBS APPLICATION </h1><br>
              <a href="http://ebsdjango4-dev.elasticbeanstalk.com/upload/">
              Assignment 4</a><br>
              <br>
              </div></body></html>'''
    return HttpResponse(temp)
              
