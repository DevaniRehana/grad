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
import os,datetime,sys
import csv
import MySQLdb
from random import randint

from boto import dynamodb2
from boto.dynamodb2.table import Table
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from boto.dynamodb2.fields import HashKey
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
REGION = 'us-west-2'


# For more information about this interface to Amazon S3, see:
# http://boto.readthedocs.org/en/latest/s3_tut.html

s3conn = boto.connect_s3(aws_access_key_id = access_key,
                     aws_secret_access_key = secret_key)
                     
#Connecting to DynamoDB
conn = boto.dynamodb.connect_to_region(
        REGION,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key)

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
    dbtime = ''
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
                      Consumer_disputed) values (%s,'%s', '%s', "%s", '%s', '%s',%s,'%s', %s, %s, '%s','%s','%s','%s')
                     '''
        rownum = 1
        newkey.get_contents_to_filename('temp.csv')
        fps3 = open('temp.csv','w')
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
                response.write( ('<br>DB Error!!'))
                response.write( '<br>'+str(e.message))
                response.write( '<br>'+str(e.args))
                continue
        et = datetime.datetime.now()
        dbtime = str(et-st)
    mydb.close()
    return dbtime,tablename 
    
#Creating a dynamoDB and inserting records  
def insertdata2dynamo(filename,newkey):
    tablename = filename.split('.')[0]
    st = datetime.datetime.now()
    #try:
    if tablename not in conn.list_tables():
        myschema=conn.create_schema(hash_key_name='FATALITY_ID',hash_key_proto_value='S')
        #Creates table 
        conn.create_table(name=tablename,schema=myschema,read_units=10,write_units=10)
        #Inserts records into the dynamo database.
    else:
        mytable = conn.get_table(tablename)
        newkey.get_contents_to_filename('abc.csv')
        ft = open('abc.csv','r')
        alldata = csv.reader(ft,delimiter=',')
        rownum = 1 
        for row in alldata:
            if rownum == 1:
                rownum = 0
                continue
            row = ['NULL' if x=='' else x for x in row]
            rowdict = {'FAT_YEARMONTH':row[0],'FAT_DAY':row[1],'FAT_TIME':row[2],
                       'FATALITY_ID':row[3],'EVENT_ID':row[4],'FATALITY_TYPE':row[5],
                       'FATALITY_DATE':row[6],'FATALITY_AGE':row[7],'FATALITY_SEX':row[8]
                       ,'FATALITY_LOCATION':row[9],'EVENT_YEARMONTH':row[10]}
            response.write(str(rowdict)+'<br>')
            data = mytable.new_item(hash_key=row[0],attrs=rowdict)
            data.put()
            #mytable.put_item(rowdict)
            #rowdata=table.new_item(hash_key=row[0], attrs=rowdict);
            #rowdata.put()        
       
    #except Exception as e:
     #   response.write( '<br>'+str(e.message))
      #  response.write( '<br>'+str(e.args))
        
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
            randzip = randint(100000,1999999)#random_with_N_digits(7)
            results = mytable.query_2(complaintid__eq=randzip)
               
        end = datetime.datetime.now()
        response.write( "<br>Time taken for "+str(rep)+" in dynamoDB is :"+str(end-start))

#Generates random queries 
def randomqueries(tablename):
    mydb = connecttosql()
    cur = mydb.cursor()
    tablename = 'harish_kamuju2'
    #qry = "select * from "+tablename+" where FATALITY_AGE >= 40"
            #qry = "select zip_code from "+tablename+" where complaint_id="+str(randzip)
    #cur.execute(qry)
    #for first query
    #for row in cur.fetchall():
     #   response.write(str(row)+'<br>')
    #for second query 
    #qry = "select count(*) from "+tablename+" where FATALITY_LOCATION like '%Open Area%' and FATALITY_SEX in ('M','F')"
    #cur.execute(qry)
    #count = cur.fetchone()
    #response.write('Count of fatalities '+str(count)+'<br>')
    #qry = "select * from "+tablename+" where FATALITY_LOCATION like '%Open Area%' and FATALITY_SEX='M'"
    #cur.execute(qry)
    #for row in cur.fetchall():
    #    response.write(str(row)+'<br>')
      #  if request.method =='POST':
            temp = '''<h2> Search from  DB</h2><br><form action ="/results/"method="post">
                  <p>Age Range from : <input type="number" name="age" value =0 /> to
                  <input type="number" name="age2" value =0 /></p>
                 <p>Gender  : <input type="text" name="gender" value ="" /></p>
                 
    
                 <p><input type="submit" /></p>'''
        response.write(temp)
        mydb.close()

#Creates a view of random tuples b/w 200-800 and generates 1k,5k,20k random search queries.
def r2queries(tablename):
    mydb = connecttosql()
    cur = mydb.cursor()
    repeats = [1000,5000,20000]
    randtuple = randint(200,800)
    for rep in repeats:
        count = 0
        newtable = 'limited'+str(randtuple)
        temp = 'create view '+newtable+' as (select * from '+tablename+' limit '+str(randtuple)+')'
        cur.execute(temp)
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
            results = mytable.query_2(ZIP_code__eq=randzip)
               
        end = datetime.datetime.now()
        response.write( "<br>Time taken for limited "+str(randtuple)+"tuples "+str(rep)+" in dynamoDB is :"+str(end-start))



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

def dynamoresult():
    print "hi"
def resultspage(request):
    response.write('''<html><body><div align='center'><br>''')
    temp = request.GET.get('tablename').split('.')
    tablename = temp[0]
    value = temp[2]
    if value == 'a4':
        response.write('''<h1>Results Page for Assignment 4
                    </h1>''')
        randomqueries(tablename)
        #r2queries(tablename)
    elif value == 'a5':
        temp = '''<h2> Search from  DB</h2><br><form action ="/result/"method="post">
              <p>Age Range from : <input type="number" name="age" value =0 /> to
              <input type="number" name="age2" value =0 /></p>
             <p>Gender  : <input type="text" name="gender" value ="" /></p>
             

             <p><input type="submit" /></p>'''
        response.write(temp)
#        temp = '''<h2> Search from Dynamo DB</h2><br><form method="post">
 #             <p>Product: <input type="text" name="product" value ="" /></p>
 #             <p>Issue  : <input type="text" name="issue" value ="" /></p>
 #             <p>ZipCode: <input type="number" name="zip" value=0 /></p>

  #            <p><input type="submit" /></p>'''
        render(request, 'results.html',{})
        dynamoqueries(tablename)
        if request.method == 'POST':
            age= request.get("age")
            age2 = request.get("age2")
            gender = request.get("gender")
            mydb = connecttosql()
            cur = mydb.cursor()
            qry = "select * from harish_kamuju2 where FATALITY_AGE between "+age+" and "+age2+" and FATALITY_SEX="+gender
            cur.execute(qry)
            for row in cur.fetchall():
                response.write(str(row)+'<br>')
     #   = request.get("mag")
      #  deci = request.get("decimal")
       # location = request.get("loc")
        #response.write('Mag:'+str(mag)+'Deci:'+str(deci)+'Loc:'+str(location))
    response.write('''</div></body></html>''')
    return response
def dynamoUpload(request):
    if request.method =='POST':
        filename = request.FILES['myfile'].name
        newkey = createkey(filename)
        start = datetime.datetime.now()
        newkey.set_contents_from_file(request.FILES['myfile'].file)
        end = datetime.datetime.now()
        uptime = str(end-start)
        fp = request.FILES['myfile'].file
        dbtime,tablename = insertdata2dynamo(fp,filename)
        return render(request, 'upresult.html',{'time':uptime,'filename':filename,'dbtime':dbtime})
    else:        
        return render(request, 'name.html',{})
        
def Upload(request):
    lvalue = request.GET.get('value')
    if request.method =='POST':
        filename = request.FILES['myfile'].name
        newkey = createkey(filename)
        start = datetime.datetime.now()
        newkey.set_contents_from_file(request.FILES['myfile'].file)
        fp = request.FILES['myfile'].file
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
              
