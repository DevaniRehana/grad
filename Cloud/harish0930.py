# -*- coding: utf-8 -*-
"""
Created on Mon Jun 08 20:27:49 2015
Name: Harish Kamuju
ID : 1001120930
Course : 6331
Lab No : 1
Section : 001
Class Timing : 6:00 - 8:00 PM

@author: Harish_Kamuju
"""

import argparse
import httplib2
import os,getpass
import sys,json,io
import hashlib
from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools
from apiclient.http import MediaIoBaseDownload
from Crypto import Random
from Crypto.Cipher import AES

USAGE = """
Usage examples:
  $ python Test2.py

"""

            
_BUCKET_NAME = 'kamuju'
_API_VERSION = 'v1'

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


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

def listobj(service):
    fields_to_return = 'nextPageToken,items(name)'
    request = service.objects().list(bucket=_BUCKET_NAME, fields=fields_to_return)
    # If you have too many items to list in one request, list_next() will
    # automatically handle paging with the pageToken.
    print "List of files in the storage:"
    while request is not None:
      resp = request.execute()
      for key in resp.values()[0]:
          print key['name']
      request = service.objects().list_next(request, resp)
    

#Exits the program from running
def exitprog(service):
    print "\nExiting the program!!"
    sys.exit(0)

#Main function which provides user interface with set of options.
#Creates a credentials file which acts like a session file
#Creates a service api to implement the functions.  
def main(argv):
    flags = parser.parse_args(argv[1:])
    storage = file.Storage('sample.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(FLOW, storage, flags)
        
    http = httplib2.Http()
    http = credentials.authorize(http)
    
    service = discovery.build('storage',_API_VERSION,http=http)
    options = {'1':listobj,'2':exitprog}
    while True:    
        print("\nSelect any of the options from the menu.\n")
        print("1:List Files\n2:Exit")
        option = raw_input("Enter the option:")
        if option not in options:
            print "Invalid option!!Please try again.\n"
            continue
        else:
            options[option](service)
            break

if __name__ == '__main__':
    main(sys.argv)