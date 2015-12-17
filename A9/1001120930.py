# -*- coding: utf-8 -*-
"""
Created on Mon Jul 06 18:25:29 2015

@author: Harish_kamuju
"""


import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
#from itertools import cycle
import numpy as np
import sys

stopwrdslist = stopwords.words('english')

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
    temp = []
    if option == 1:
        temp = df[23].tolist()
        #temp = ['None' for w in temp if math.isnan(w) ]
        temp = [str(w).lower() for w in temp]
    elif option == 2:
        temp = df[22].tolist()
        temp = [str(w).lower() for w in temp]
    elif option == 3:
        temp = df[6].tolist()
        temp = [str(w).lower() for w in temp]
    elif option == 4:
        temp = df[7].tolist()
        temp = [str(w).lower() for w in temp]
    elif option == 5:
        temp = df[8].tolist()
        temp = [str(w).lower() for w in temp]
    elif option == 6:
        temp = df[11].tolist()
        temp = [str(w).lower() for w in temp]
    
    vectorizer = TfidfVectorizer(stop_words='english')
    Xfit = vectorizer.fit_transform(temp)
    kmeans = KMeans(n_clusters=clusters, init='k-means++', max_iter=20, n_init=1)
    km = kmeans.fit(Xfit)
  
    reduced_data = km.cluster_centers_
    centroids = PCA(n_components=2).fit_transform(reduced_data)
   
    plt.scatter(centroids[:, 0], centroids[:, 1],
            marker='x', s=140, linewidths=1,
            color='b', zorder=1)
    # Step size of the mesh. Decrease to increase the quality of the VQ.
    h = 1.02     # point in the mesh [x_min, m_max]x[y_min, y_max].
    
    # Plot the decision boundary. For that, we will assign a color to each
    x_min, x_max = reduced_data[:, 0].min() + 1, reduced_data[:, 0].max() - 1
    print x_min, x_max
    y_min, y_max = reduced_data[:, 1].min() + 1, reduced_data[:, 1].max() - 1
    print y_min, y_max
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    print xx, yy 
    
    sys.exit(0)
    # Obtain labels for each point in mesh. Use last trained model.
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    
    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.figure(1)
    plt.clf()
    plt.imshow(Z, interpolation='nearest',
               extent=(xx.min(), xx.max(), yy.min(), yy.max()),
               cmap=plt.cm.Paired,
               aspect='auto', origin='lower')
    
    plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
    plt.title('K-means clustering on the dataset (PCA-reduced data)\n'
          'Centroids are marked with blue cross')
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xticks(())
    plt.yticks(())
    plt.show()
    
    

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
            
        
