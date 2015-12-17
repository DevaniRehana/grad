
#------------------------------------------------------------------
# Name: Rahul Rayineni
# ID: 1001051819
# Course: CSE 6331-002
# Assignment-2: Uploading and Dowloading files to Amazon S3
#------------------------------------------------------------------

import boto
import os
import Tkinter
import tkFileDialog
import time
import datetime
import boto.s3
from boto.s3.key import Key
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

#Get the IAM user credentials
AWS_ACCESS_KEY_ID = 'AKIAJNXBIPVXLQ4A2PTQ'
AWS_SECRET_ACCESS_KEY = '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'

#connecting to Amazon S3 service.
conn = boto.connect_s3(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
print "Successfully Connected to Amazon S3"

#Creating a bucket in Amazon
bucket = conn.create_bucket("rayinenicloud")

#generating a key
key1 = Key(bucket)

#Set the key for the file
key1.key = 'all_month.csv'

#select the file with filedialog window that you want to upload to s3
print "Select earthquake information file to upload to S3"
Tkinter.Tk().withdraw() # Close the root window
file_path = tkFileDialog.askopenfilename()
time.sleep(2)

#set timer to calculate time difference
start = datetime.datetime.now().replace(microsecond=0)

print "uploading...please wait...."

#Upload the file to the AWS s3
key1.set_contents_from_filename(file_path)

end = datetime.datetime.now().replace(microsecond=0)
#print the time taken to upload the file

print "Time taken to upload files"
print (end - start)


'''  
    The following part of code is for 
    downloading the file from amazon S3 to local file System and calculating the download time.
'''

print "downloading from amazon s3..."

#set the timer
download_start = datetime.datetime.now().replace(microsecond=0)

#get the key for the file
key = conn.get_bucket('rayinenicloud').get_key('all_month.csv')

#download the contents of the file
key.get_contents_to_filename('C:\\Users\\rayin_000\\Desktop\\rahul.csv')

download_end = datetime.datetime.now().replace(microsecond=0)

print "time taken to download"
print (download_end-download_start)


print("donwload success..")




