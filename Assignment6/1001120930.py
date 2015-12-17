# -*- coding: utf-8 -*-
"""
Created on Mon Jul 06 18:25:29 2015

@author: Harish_kamuju
"""

import sys
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def main(option):
    try:
        clusters = int(raw_input('Enter the number of clusters:'))
    except:
        print 'Invalid Cluster Number'
        return
    df = pd.read_csv('Consumer2.csv',header=None)#, delim_whitespace=True)
    #state = df[23],City = df[22]
    #product category = df[6]
    #product subcat = df[7]
    #product type = df[8]
    #brand = df[11]
    
    

if __name__ == "__main__":
    while True:
        print "Select from the list to Cluster:"
        try:
            option = int(raw_input('''1.State\n2.City\n3.Product Category\n4.Product SubCategory\n5.Product Type\n6.Brand\n7.Exit\nInput:'''))
        except:
            print 'Invalid Option. Exiting!'
            break
        if option in range(1,7):
            main(option)
            break
        else:
            print 'Exiting!!!'
            break
    #sys.exit(0)
            
        
