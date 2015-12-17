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

#bucket = s3.create_bucket(bucket_name)
def downloadfiles():
    filename = raw_input("Enter the filename to dump data into Database:\n")
    if buck.get_key(filename):
        fkey = createkey(filename)
        fkey.get_contents_to_filename(filename)
        return filename
    else:
        print "No file in the bucket.Exiting!!\n"
        sys.exit(0)
        
def connecttosql():
    mydb = MySQLdb.connect(host = "awsdb.cppwhxblopbz.us-west-2.rds.amazonaws.com",
                     user="kamuju",passwd="password", port=3306, db="govdata")
    if mydb == None:
        print ' Unable to connect to DataBase.Please try again later!'
    else:
        cur = mydb.cursor()
        tablename = "consumer_complaints22"
        cur.execute("show tables like '"+tablename+"'")
        row = cur.fetchone()
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