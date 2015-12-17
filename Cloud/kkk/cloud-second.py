__author__ = 'kaushika'
import argparse
import httplib2
import os
import sys
import json
import time
import datetime
import io
import hashlib
#Google apliclient (Google App Engine specific) libraries.
from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools
#from apiclient.http import MediaIoBaseDownload
#pycry#pto libraries.
from Crypto import Random
from Crypto.Cipher import AES
import csv
_BUCKET_NAME = 'kaushikabucket' #name of your google bucket.
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
def main(argv):
   #put(service)
   flags = parser.parse_args(argv[1:])


  #sample.dat file stores the short lived access tokens, which your application requests user data, attaching the access token to the request.
  #so that user need not validate through the browser everytime. This is optional. If the credentials don't exist
  #or are invalid run through the native client flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file (sample.dat in this case).
   storage = file.Storage('sample.dat')
   credentials = storage.get()
   if credentials is None or credentials.invalid:
    credentials = tools.run_flow(FLOW, storage, flags)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
   http = httplib2.Http()
   http = credentials.authorize(http)

  # Construct the service object for the interacting with the Cloud Storage API.
   service = discovery.build('storage', _API_VERSION, http=http)
#def put(service):
   starting_time=time.time()
   fileupload=raw_input("please enter the name of the file")

   req = service.objects().insert(
        bucket=_BUCKET_NAME,
        name=fileupload,media_body='all_month.csv')
   resp = req.execute()
   ending_time=time.time()-starting_time
   print ending_time
   fields_to_return = 'nextPageToken,items(bucket,name,metadata(my-key))'

   print json.dumps(resp, indent=2)


if __name__ == '__main__':
    main(sys.argv)
