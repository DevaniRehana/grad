# -*- coding: utf-8 -*-
"""
Created on Tue Jun 09 18:42:48 2015

@author: Home
"""

import argparse
import httplib2
import os
import sys,json,time,datetime,io
import hashlib,struct
from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools
from apiclient.http import MediaIoBaseDownload
from Crypto import Random
from Crypto.Cipher import AES

password ='googlecloud'
key = hashlib.sha256(password).digest()
chunksize=1024*1024

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
    
    
if __name__ == "__main__":
    #enct = encrypt_file('ab.txt',key)
    dect = decrypt_file('encab.txt',key)