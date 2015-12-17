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
import memcache


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

# Everything uploaded to Amazon S3 must belong to a bucket. These buckets are
# in the global namespace, and must have a unique name.
#
# For more information about bucket name restrictions, see:
# http://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html
mybucket = "kamuju"
print "Using bucket : " + mybucket
buck = s3conn.get_bucket(mybucket)
memc = memcache.Client(['127.0.0.1:11211'], debug=1)

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
        print "No file in the bucket.Exiting!!\n"
        sys.exit(0)
#Connects to RDS of AWS        
def connecttosql():
    try:    
        mydb = MySQLdb.connect(host = "awsdb.cppwhxblopbz.us-west-2.rds.amazonaws.com",
                     user="kamuju",passwd="password", port=3306, db="govdata")
        if mydb == None:
            print ' Unable to connect to DataBase.Please try again later!Exiting'
            sys.exit(0)
        else:
            return mydb
    except Exception as e:
        print (e.message)
        print (e.args)
        
#Inserts tables into RDS    
def insertdata():
    
    mydb = connecttosql()
    cur = mydb.cursor()
    tablename = "consumer_complaints22"
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
        print "No records in the table\n"
        filename = downloadfiles()
        print "Inserting data from the CSV to table\n"
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
        fp = open(filename,'r')
        alldata = csv.reader(fp,delimiter=',')
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
                print ('DB Error!!')
                print (e.message)
                print (e.args)
                continue
        et = datetime.datetime.now()
    print 'Time taken to insert into DB:'+str(et-st)
    mydb.close()


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
            #print count,randzip
            qry = "select Product,Issue,ZIP_code from "+tablename+" where ZIP_code="+str(randzip)
            #qry = "select zip_code from "+tablename+" where complaint_id="+str(randzip)
            cur.execute(qry)
            
        end = datetime.datetime.now()
        print "Time taken for "+str(rep)+" is :"+str(end-start)
    mydb.close()

#Creates a view of random tuples b/w 200-800 and generates 1k,5k,20k random search queries.
def r2queries(tablename):
    mydb = connecttosql()
    cur = mydb.cursor()
    repeats = [1000,5000,20000]
    
    for rep in repeats:
        count = 0
        randtuple = randint(200,800)
        newtable = 'limited'+str(randtuple)
        temp = 'create view '+newtable+' as (select * from '+tablename+' limit '+str(randtuple)+')'
        cur.execute(temp)
        mydb.commit()
        start = datetime.datetime.now()
        while count < rep:
            count +=1
            randzip = randint(10000,99999)
            #print count,randzip
            qry = "select Product,Issue,ZIP_code from "+newtable+" where ZIP_code="+str(randzip)
            #qry = "select zip_code from "+tablename+" where complaint_id="+str(randzip)
            cur.execute(qry)
            
        end = datetime.datetime.now()
        print "Time taken for limited "+str(randtuple)+"tuples "+str(rep)+" is :"+str(end-start)
    mydb.close()        

#Creates key for the filename         
def createkey(filename):
    newkey = Key(buck)
    newkey.key = filename
    return newkey
#Lists all the buckets in the s3
def listbuckets():
    print "List of buckets:"
    for bucket in s3conn.get_all_buckets():
        print bucket

#uploads the files to bucket
def uploadtobucket():
    filename = raw_input("Enter the filename to upload:\n")
    if not os.path.isfile(filename):
        print "No file ["+filename+"] in the current dir["+os.getcwd()+"].\n"
    else:
        # Files in Amazon S3 are called "objects" and are stored in buckets. A specific
        # object is referred to by its key (i.e., name) and holds data. Here, we create
        # a new object with the key as filename so user is prompted if a file already exists. 
        if buck.get_key(filename):
            print "File already exists!!.Enter a different file name\n"
            uploadtobucket()
        else:
            newkey = createkey(filename)
            start = datetime.datetime.now()
            fp = open(filename,'r')
            fsize = os.fstat(fp.fileno()).st_size
            if  fsize > 5242880L: #If file size greater than 5MB
                upbytes=newkey.set_contents_from_file(fp)
            else:
                upbytes=newkey.set_contents_from_filename(filename)
            end = datetime.datetime.now()
        if upbytes == fsize:
            print '''Uploaded the file ['''+filename+'''] successfully.\n
                     Time taken to upload: '''+str(end-start)
        else:
            print "Upload Failed!!"
                     
        
def main():
    listbuckets()
    uploadtobucket()
    downloadfiles()
    randomqueries('consumer_complaints2')
    r2queries('consumer_complaints2')     
    
if __name__ =="__main__":
    main()
