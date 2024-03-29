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
import datetime,sys
import csv
import MySQLdb
from random import randint
from boto.dynamodb2.table import Table
from django.shortcuts import render
from django.http import HttpResponse
import boto.dynamodb.condition as cndt

reload(sys)
sys.setdefaultencoding("utf-8")

#from elasticache_pyclient import MemcacheClient
#import memcache
boto.connect_dynamodb()
#mc = memcache.Client(['a4cache.5odawy.cfg.usw2.cache.amazonaws.com:11211'],debug=1)

# Instantiate a new client for Amazon Simple Storage Service (S3). With no
# parameters or configuration, the AWS SDK for Python (Boto) will look for
# access keys in these environment variables:
#
access_key='AKIAINOHI7FXQD6PMNPA'
secret_key='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'
#REGION = 'us-west-2'
REGION = 'us-east-1'


# For more information about this interface to Amazon S3, see:
# http://boto.readthedocs.org/en/latest/s3_tut.html

s3conn = boto.connect_s3(aws_access_key_id = access_key,
                     aws_secret_access_key = secret_key)
                     
#Connecting to DynamoDB
conn = boto.dynamodb.connect_to_region(REGION,aws_access_key_id=access_key,aws_secret_access_key=secret_key)

response = HttpResponse()
# Everything uploaded to Amazon S3 must belong to a bucket. These buckets are
# in the global namespace, and must have a unique name.
mybucket = "kamuju"
buck = s3conn.get_bucket(mybucket)
#memc = memcache.Client(['127.0.0.1:11211'], debug=1)
   
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
def insertdata(filename,newkey):
    mydb = connecttosql()
    cur = mydb.cursor()
    tablename = filename.split('.')[0]
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
        #response.write( "<br>No records in the table") 
        #response.write( "<br>Inserting data from the CSV to table")
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
                      Consumer_disputed) values (%s,'%s', '%s', "%s", '%s', 
                      '%s',%s,'%s', %s, %s, '%s','%s','%s','%s')
                     '''
        rownum = 1
        newkey.get_contents_to_filename('temp.csv')
        fps3 = open('temp.csv','r')
        alldata = csv.reader(fps3,delimiter=',')
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
                continue
        et = datetime.datetime.now()
    dbtime = str(et-st)
    mydb.close()
    return dbtime,tablename 
    
#Creating a dynamoDB and inserting records  
def insertdata2dynamo(filename,newkey):
    tablename = filename.split('.')[0]
    return "09:13:45.454321",tablename
    st = datetime.datetime.now()
    #try:
    if tablename not in conn.list_tables():
        myschema=conn.create_schema(hash_key_name='complaintid',hash_key_proto_value='S')
        #Creates table 
        conn.create_table(name=tablename,schema=myschema,read_units=1,write_units=1)
        
    mytable = conn.get_table(tablename)
    newkey.get_contents_to_filename('temp.csv')
    items =[]
    with open('temp.csv', 'rb') as ft:
        alldata = csv.reader(ft,delimiter=',')
        rownum = 1 
        #Inserts records into the dynamo database.
        for row in alldata:
            if rownum == 1:
                rownum = 0
                continue
            row = ['NULL' if x=='' else x for x in row]
            rowdict = {'complaintid':row[0],'Product':row[1],'Subproduct':row[2],
                       'Issue':row[3],'Subissue':row[4],'State':row[5],
                       'ZIP_code':row[6],'Submitted_via':row[7],'Date_received':row[8],
                   'Date_sent_to_company':row[9] ,'Company':row[10],'Company_response':row[11],
                   'Timely_response':row[12] ,'Consumer_disputed':row[13]}
            try:
                data = mytable.new_item(hash_key=row[0],attrs=rowdict)
                items.append(data)
            except Exception as e:
                response.write(str(e.message))
                continue
            if len(items) == 25:
                batch_items = items[:25]
                batch_list = conn.new_batch_write_list()
                batch_list.add_batch(mytable, batch_items)
                conn.batch_write_item(batch_list)
                items = []

                        
    et = datetime.datetime.now()
    dbtime = str(et-st)
    return dbtime,tablename

def dynamoqueries(tablename):
    mytable = Table(tablename,connection=conn)
    repeats = [1000,5000,20000]
    for rep in repeats:
        count = 0
        start = datetime.datetime.now()
        while count < rep:
            count +=1
            randzip = randint(1000,99999)#random_with_N_digits(7)
            results = mytable.scan(scan_filter={'ZIP_code':cndt.CONTAINS(randzip)})
            
            
        end = datetime.datetime.now()
        response.write( "<br>Time taken for "+str(rep)+" in dynamoDB is :"+str(end-start))

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
    newtable = 'limited'+str(randtuple)
    temp = 'DROP view '+newtable
    cur.execute(temp)
    mydb.commit()
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
        response.write( "<br>Time taken for limited "+str(randtuple)+" tuples "+str(rep)+" is :"+str(end-start))
    mydb.close()        

#
def dynamor2queries(tablename):
    mytable = Table(tablename,connection=conn)
    randtuple = randint(200,800)
    repeats = [1000,5000,20000]
    for rep in repeats:
        count = 0
        start = datetime.datetime.now()
        while count < rep:
            count +=1
            randzip = randint(10000,99999)#random_with_N_digits(7)
            results = mytable.scan(scan_filter={'ZIP_code':cndt.CONTAINS(randzip)})
        end = datetime.datetime.now()
        response.write( "<br>Time taken for limited "+str(randtuple)+" tuples "+str(rep)+" in dynamoDB is :"+str(end-start))

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

def dynoresult(request):
    #prd = request.GET.get("product")
    #issu= request.GET.get("issue")
    zipc = request.GET.get("zip")
    response.write('''<div align="center"><h1> List of records with the search query ZIP_code as:</h1>'''+str(zipc))
    mytable = Table('Consumer_Complaints60k',connection=conn)
    results = mytable.scan(scan_filter={'ZIP_code':cndt.CONTAINS(zipc)})
    results = mytable.scan()
    response.write('''<br><table border="1" >
  <tr>
    <td>ComplaintID</td><td>Product</td><td>SubProduct</td><td>Issue</td><td>Subissue</td>
    <td>State</td><td>ZipCode</td><td>Submitted_via</td><td>Date_received</td><td>Date_sent_to_company</td>
    <td>Company</td><td>Company_response</td><td>Timelyresponse</td><td>Consumer_disuputed</td>
  </tr>''')    
    for row in results:
        response.write('''<tr>
            <td>'''+row['complaintid']+'''</td><td>'''+str(row['Product'])+'''</td><td>'''+str(row['Subproduct'])+
            '''</td><td>'''+str(row['Issue'])+'''</td><td>'''+str(row['Subissue'])+'''</td><td>'''+row['State']+
            '''</td><td>'''+str(row['ZIP_code'])+'''</td><td>'''+str(row['Submitted_via'])+'''</td><td>'''+str(row['Date_received'])+
            '''</td><td>'''+str(row['Date_sent_to_company'])+'''</td><td>'''+row['Company']+'''</td><td>'''+row['Company_response']+
            '''</td><td>'''+row['Timely_response']+'''</td><td>'''+row['Consumer_disputed']+'''</td>
            </tr>''')
    response.write('''</div>''')   
    return response
def searchpage(request):
    return render(request, 'results.html')
        
def resultspage(request):
    response.write('''<html><body><div align='center'><br>''')
    temp = request.GET.get('tablename').split('.')
    tablename = temp[0]
    value = temp[2]
    if value == 'a4':
        response.write('''<h1>Results Page for Assignment 4
                    </h1>''')
        randomqueries(tablename)
        r2queries(tablename)
    elif value == 'a5':
#        temp = '''<h2> Search from Dynamo DB</h2><br><form method="post">
 #             <p>Product: <input type="text" name="product" value ="" /></p>
 #             <p>Issue  : <input type="text" name="issue" value ="" /></p>
 #             <p>ZipCode: <input type="number" name="zip" value=0 /></p>

  #            <p><input type="submit" /></p>'''
        response.write('<br> <h1> Dynamo DB search results </h1>')
        dynamoqueries(tablename)
        dynamor2queries(tablename)
        response.write('''<br> <a href ='/final/'> Go to search Engine for DB </a><br>''')
     #   mag = request.get("mag")
      #  deci = request.get("decimal")
       # location = request.get("loc")
        #response.write('Mag:'+str(mag)+'Deci:'+str(deci)+'Loc:'+str(location))
    response.write('''</div></body></html>''')
    return response
        
def Upload(request):
    lvalue = request.GET.get('value')
    if request.method =='POST':
        filename = request.FILES['myfile'].name
        newkey = createkey(filename)
        start = datetime.datetime.now()
        newkey.set_contents_from_file(request.FILES['myfile'].file)
        end = datetime.datetime.now()
        uptime = str(end-start)  
        if  lvalue == 'a4':
            dbtime,tablename = insertdata(filename,newkey)
        elif lvalue == 'a5':
            dbtime,tablename = insertdata2dynamo(filename,newkey)
        return render(request, 'upresult.html',{'time':uptime,'filename':filename,'dbtime':dbtime,'value':lvalue})
    else:        
        return render(request, 'name.html',{'value':lvalue})

    
def Homepage(request):
    return render(request,'index.html',{'linka4':'a4','linka5':'a5'})
              
