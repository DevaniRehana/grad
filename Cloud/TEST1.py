# -*- coding: utf-8 -*-
"""
Created on Mon Jun 08 20:27:49 2015

@author: Harish_Kamuju
"""

import argparse
import httplib2
import os,getpass
import sys,json,io
import hashlib
from struct import pack
from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools
from apiclient.http import MediaIoBaseDownload
from apiclient.http import MediaFileUpload
from Crypto import Random
from random import randint
from Crypto.Cipher import Blowfish
from Crypto.Cipher import AES

bs = Blowfish.block_size
USAGE = """
Usage examples:
  $ python TEST1.py

"""
    

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


#password ='googlecloud'
#key = hashlib.sha256(password).digest()
#key = hashlib.md5(password).hexdigest()


chunksize=1024*1024
DEFAULT_MIMETYPE = 'application/octet-stream'




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
def put(service,filename,encrypted_file):
  try:
    #encrypted_file = encrypt_file(filename, key)
    #media = MediaFileUpload(filename, chunksize, resumable=True)
    #if not media.mimetype():
    #    media = MediaFileUpload(filename, DEFAULT_MIMETYPE, resumable=True)
    request = service.objects().insert(
        bucket=_BUCKET_NAME,
        name=filename,
        media_body=encrypted_file)
    resp = request.execute()
    #os.remove(filename) 
    #os.remove(encrypted_file)
    #print json.dumps(resp, indent=2)
  except client.AccessTokenRefreshError:
    print ("Error in the credentials")

def listlocal(service):
    print "List of files in the local folder are:\n"
    for root, directories, files in os.walk('.'):
        print files
def listobj(service):
    fields_to_return = 'nextPageToken,items(name,size,contentType,metadata(my-key))'
    request = service.objects().list(bucket=_BUCKET_NAME, fields=fields_to_return)
    # If you have too many items to list in one request, list_next() will
    # automatically handle paging with the pageToken.
    while request is not None:
      resp = request.execute()
      print json.dumps(resp, indent=2)
      request = service.objects().list_next(request, resp)
      
def decrypt(service,mastkey,key):
    get(service,'keysfish.tmp')
    for root, directories, files in os.walk('.'):
        for filename in files:
            if filename.endswith('.txt') or filename.endswith('.jpg'):
                with open(filename,'rb') as infile:
                    plaintext = infile.read()
                infile.close()
                plen = bs - divmod(len(plaintext),bs)[1]
                padding = [plen]*plen
                padding = pack('b'*plen, *padding)
                msg = iv + cipher.decrypt(plaintext + padding)
                encf = filename[3:]           
                fenc = open(encf,'w')
                fenc.write(msg)
                fenc.close()
    
def exitprog(service):
    print "\nExiting the program!!"
    sys.exit(0)

def main(argv):
    flags = parser.parse_args(argv[1:])
    storage = file.Storage('sample.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(FLOW, storage, flags)
        
    http = httplib2.Http()
    http = credentials.authorize(http)
    
    service = discovery.build('storage',_API_VERSION,http=http)
    key = getpass.getpass("Enter master key.\n:")
    
    randomNo = random_with_N_digits(5)
    masterkey = key+str(randomNo)
    iv = Random.new().read(bs)
    cipher = Blowfish.new(masterkey, Blowfish.MODE_CBC, iv)
    fp = open('keysfish.tmp','w')
    for root, directories, files in os.walk('.'):
        for filename in files:
            if filename.endswith('.txt') or filename.endswith('.jpg'):
                print filename
                temp = filename+","+str(randomNo)+"\n"
                fp.write(str(temp))
                with open(filename,'rb') as infile:
                    plaintext = infile.read()
                infile.close()
                plen = bs - divmod(len(plaintext),bs)[1]
                padding = [plen]*plen
                padding = pack('b'*plen, *padding)
                msg = iv + cipher.encrypt(plaintext + padding)
                encf = 'enc'+filename            
                fenc = open(encf,'w')
                fenc.write(msg)
                fenc.close()
                put(service,filename,filename)
                os.remove(filename)
    fp.close()
    
    put(service,'keysfish.tmp','keysfish.tmp')
      
    options = {'1':listlocal,'2':decrypt,'3':listobj,'4':exitprog}
    while True:    
        print("\nSelect any of the options from the menu.\n")
        print("1:List Local Files\n2:Decrypt Files\n3:List Cloud Files\n\n4:Exit")
        option = raw_input("Enter the option:")
        if option not in options:
            print "Invalid option!!Please try again.\n"
            continue
        else:
            if option == '2':
                mastkey= raw_input("enter the key\n")
                if mastkey == key:
                    options[option](service,mastkey,key)
                else:
                    print "Invalid key provided.Exiting"
                    sys.exit(0)
            else:
                options[option](service)
            break

if __name__ == '__main__':
    main(sys.argv)
