# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 15:29:42 2015

@author: Harish_Kamuju
"""
import cgi
import webapp2
import MySQLdb
import os,json,sys
import jinja2
import datetime
import argparse
import httplib2
#from google.appengine.ext.webapp.util import run_wsgi_app
from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools
from apiclient.http import MediaIoBaseDownload
from apiclient.http import MediaFileUpload


_BUCKET_NAME = 'kamuju'
_API_VERSION = 'v1'

#First Connecting to Cloud Storage 
# client_secret.json is the JSON file that contains the client ID and Secret.
#You can download the json file from your google cloud console.
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secret.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. 
# These scopes are used to restrict the user to only specified permissions (in this case only to devstorage) 
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/devstorage.full_control',
      'https://www.googleapis.com/auth/devstorage.read_only',
      'https://www.googleapis.com/auth/devstorage.read_write',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])

#Uploads a file to google cloud storage
def put(service,filename):
  try:
      start = datetime.datetime.now()
      media = MediaFileUpload(filename,mimetype=None,chunksize=1024*1024, resumable=True)
      #if not media.mimetype():
      #    media = MediaFileUpload(filename, DEFAULT_MIMETYPE, resumable=True)
      request = service.objects().insert(bucket=_BUCKET_NAME,
                name=filename,media_body=media)
      request.execute()
      end = datetime.datetime.now()
    #os.remove(filename)
    #print json.dumps(resp, indent=2)
  except client.AccessTokenRefreshError:
      print ("Error in the credentials")
  print "Uploaded the file "+filename+" successfully!\n"
  print "Time take to upload:",(end-start)

def listobj(service):
    fields_to_return = 'nextPageToken,items(name,size,contentType,metadata(my-key))'
    request = service.objects().list(bucket=_BUCKET_NAME, fields=fields_to_return)
    # If you have too many items to list in one request, list_next() will
    # automatically handle paging with the pageToken.
    while request is not None:
      resp = request.execute()
      print json.dumps(resp, indent=2)
      request = service.objects().list_next(request, resp)

def deleteobj(service,filename):
  try:
    service.objects().delete(
        bucket=_BUCKET_NAME,
        object=filename).execute()
    print filename+" deleted"
  except client.AccessTokenRefreshError:
    print ("Error in the credentials")

def exitprog(service):
    print "\nExiting the program!!"
    sys.exit(0)
    
def connect2cloud():
    env = os.getenv('SERVER_SOFTWARE')
    if (env and env.startswith('Google App Engine/')):
        # Connecting from App Engine
        db = MySQLdb.connect(
        unix_socket='/cloudsql/wide-plating-97021:cloudkamuju',
        db='testdb',
        user='root')
    else:
        # Connecting from an external network.
        # Make sure your network is whitelisted
        db = MySQLdb.connect(
        host='173.194.233.83',
        port=3306,
        user='root')

    cur = db.cursor()
    cur.execute('DESC quakes')

def main(argv):
    flags = parser.parse_args(argv[1:])
    storage = file.Storage('sample.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(FLOW, storage, flags)
        
    http = httplib2.Http()
    http = credentials.authorize(http)
    
    service = discovery.build('storage',_API_VERSION,http=http)
    options = {'1':put,'2':exitprog,'3':listobj,'4':deleteobj,
               '5':connect2cloud,'6':exitprog}
    while True:    
        print("\nSelect any of the options from the menu.\n")
        print("1:Upload CSV file\n2:Download\n")
        print("3:List Files in Cloud\n4:Delete\n6:Exit")
        print("5:Connect to Cloud SQL\n")
        option = raw_input("Enter the option:")
        if option not in options:
            print "Invalid option!!Please try again.\n"
            continue
        else:
            if option in ['3','6']:
                options[option](service)
            elif option in ['5']:
                options[option]()
            else:
                filename = raw_input("\nEnter the filename with extension:")
                options[option](service,filename)

if __name__ == '__main__':
    main(sys.argv)