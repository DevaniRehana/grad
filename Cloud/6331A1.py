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
  $ python 6331A1.py

"""
password = getpass.getpass("Enter the password to generate the key.\n:")
#password ='googlecloud'
key = hashlib.sha256(password).digest()
#key = hashlib.md5(password).hexdigest()


chunksize=1024*1024
DEFAULT_MIMETYPE = 'application/octet-stream'


def pad(s):
    return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

def encrypt(message, key, key_size=256):
    message = pad(message)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key,AES.MODE_CBC, iv)
    return iv + cipher.encrypt(message)

def decrypt(ciphertext,key):
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    return plaintext.rstrip(b"\0")

def encrypt_file(file_name, key):
    print 'Encrypting the file...'   
    encrypfile = 'enc'+file_name
    #filesize = os.path.getsize(file_name)
    with open(file_name,'rb') as infile:
        plaintext = infile.read()
    infile.close()
    encryptedtext = encrypt(plaintext, key)
    with open(encrypfile, 'wb') as outfile:
        outfile.write(encryptedtext)
    outfile.close()
    return encrypfile

def decrypt_file(file_name, key):
    print 'Decrypting the File...'
    decrypfile = 'dec'+file_name
    with open(file_name,'rb') as infile:
        encrypttext = infile.read()
    infile.close()
    decryptedtext = decrypt(encrypttext,key)
    with open(decrypfile,'wb') as outfile:
        outfile.write(decryptedtext)
        #origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
            #outfile.truncate(origsize)
    outfile.close()
    return decrypfile
            
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

#Downloads the files from cloud storage and decrypts them provided the key.
def get(service,filename):
    try:
        request=service.objects().get(
                bucket=_BUCKET_NAME,
                object= filename,
                fields='bucket,name,metadata(my-key)',)
        resp = request.execute()
        print json.dumps(resp, indent=2)
        
        request = service.objects().get_media(bucket=_BUCKET_NAME,object=filename)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh,request,chunksize)
        done = False
        while not done:
            status,done = downloader.next_chunk()
            if status:
                print 'Download %d%%' % int(status.progress() * 100)
            print 'Download Complete!'
        decode = decrypt(fh.getvalue(),key)
        with open(filename, 'wb') as fileout:
             fileout.write(decode)
        
    except client.AccessTokenRefreshError:
        print "Error in the credentials"

#uploads the files to the cloud storage upon encryption provided the filename and key
def put(service,filename):
  try:
    encrypted_file = encrypt_file(filename, key)
    #media = MediaFileUpload(filename, chunksize, resumable=True)
    #if not media.mimetype():
    #    media = MediaFileUpload(filename, DEFAULT_MIMETYPE, resumable=True)
    request = service.objects().insert(
        bucket=_BUCKET_NAME,
        name=filename,
        media_body=encrypted_file)
    resp = request.execute()
    os.remove(filename) 
    os.remove(encrypted_file)
    print json.dumps(resp, indent=2)
  except client.AccessTokenRefreshError:
    print ("Error in the credentials")

#Lists all the files including directories and files in the directories
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
    
#Deletes a particular file when the filename is given by the user
def deleteobj(service,filename):
  try:
    service.objects().delete(
        bucket=_BUCKET_NAME,
        object=filename).execute()
    print filename+" deleted"
  except client.AccessTokenRefreshError:
    print ("Error in the credentials")

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
    options = {'1':put,'2':get,'3':listobj,'4':deleteobj,'5':exitprog}
    while True:    
        print("\nSelect any of the options from the menu.\n")
        print("1:Upload\n2:Download\n3:List Files\n4:Delete\n5:Exit")
        option = raw_input("Enter the option:")
        if option not in options:
            print "Invalid option!!Please try again.\n"
            continue
        else:
            if option in ['3','5']:
                options[option](service)
            else:
                filename = raw_input("\nEnter the filename with extension:")
                options[option](service,filename)
            break

if __name__ == '__main__':
    main(sys.argv)