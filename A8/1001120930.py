# -*- coding: utf-8 -*-
"""
Created on Mon Jul 06 18:25:29 2015

@author: Harish_kamuju
"""


import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import sklearn
from sklearn.cluster import KMeans
#from nltk.corpus import stopwords
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
#from itertools import cycle
import numpy as np
import sys

#stopwrdslist = stopwords.words('english')

def main(option):
    try:
        clusters = int(raw_input('Enter the number of clusters:'))
    except:
        print 'Invalid Cluster Number'
        return
    df = pd.read_csv('harishkamuju.csv',skiprows=[0],header=None)#, delim_whitespace=True)
#survived = row[1], sex = row[3],age=row[4],dest= row[13]
    if option == 1:
        temp = pd.get_dummies(df[3],df[4]) 
    elif option == 2:
        temp = pd.get_dummies(df[4],df[13])
    elif option == 3:
        temp = pd.get_dummies(df[13],df[3])
    
    mat = temp.as_matrix()
    km = sklearn.cluster.KMeans(n_clusters=clusters)
    km.fit(mat)
    labels = km.labels_
    results = pd.DataFrame([temp.index,labels]).T
    if option == 1:
        results['Sex'] = df[3]
    elif option == 2:
        results['Age'] = df[4]
    elif option == 3:
        results['Destination'] = df[13]
 
    print "Clusters :"
    print results
    reduced_data = km.cluster_centers_
    print "Cluster Centers:"
    print reduced_data
    centroids = PCA(n_components=2).fit_transform(reduced_data)
    
    plt.scatter(centroids[:, 0], centroids[:, 1],
            marker='o', s=160, linewidths=2,
            color='b', zorder=1)
    plt.show()
    
    

if __name__ == "__main__":
    while True:
        print "Select from the list to Cluster:"
        try:
            option = int(raw_input('''1.Sex n Age\n2.Age n Dest \n3.Destination and Sex\n7.Exit\nInput:'''))
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
            
        
