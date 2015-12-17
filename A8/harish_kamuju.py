# -*- coding: utf-8 -*-
"""
Created on Mon Jul 06 18:05:58 2015

@author: Home
"""

import sys,os,nltk,re,string
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from nltk import stem
import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel

from sklearn.decomposition import PCA

more_stop_words = ['cant','didnt','doesnt','dont','goes','isnt','hes',\
'shes','thats','theres','theyre','wont','youll','youre','youve',\
're','tv','g','us','en','ve','vg','didn','pg','gp','our','we',
'll','film','video','name','years','days','one','two','three',\
'four','five','six','seven','eight','nine','ten','eleven','twelve','rt'] 
dictTweets = {}
listTweets = []
finalClusters = {}

def main():
    print "In Main..."
    stopwrdslist = stopwords.words('english') + more_stop_words
    #fp = open('OscarTweets_full2.txt','r')
    #fp = open('t200.txt','r')
    #Below line to be uncommented for clustering all the tweets
    #fp = open('finalprocessedtweets.txt','r')
    #Testing for first 200 tweets
    fp = open('t200.txt','r')
    lines = fp.readlines()
    fp.close()
    
    for line in lines[1:]:
        temp = str(line.strip("\n"))
        desc = re.sub('[\r\n]','',temp) #removing \r and \n trailing characters
        desc = desc.replace("\n",'')
        splremoved = re.compile('[%s]' % re.escape(string.punctuation)).sub(" ",desc) #removing punctuations
        #removeNum = re.compile('[\d]+').sub("",splremoved)
        #words = removeNum.lower().split()
        words = splremoved.lower().split() #converting to lower case
        filterwords = [w for w in words if not w in stopwrdslist and len(w) > 1]
        sentence = ' '.join(filterwords)
        listTweets.append(sentence)
        fileno = lines.index(line)
        dictTweets[fileno] = sentence
    print "Pre-processing done!"
    #change the true_k value for the number of clusters. Here 10 clusters are 
    #considered
    true_k = 10    
    vectorizer = TfidfVectorizer(stop_words='english')
    Xfit = vectorizer.fit_transform(listTweets)
    model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
    km = model.fit(Xfit)
    
    index = 0
    for clustNo in km.labels_:
        if clustNo not in finalClusters:
            finalClusters[clustNo] = [index]
        else:
            finalClusters[clustNo].append(index)
        index += 1
   
    for clustno in finalClusters:
        filename = 'cluster'+str(clustno+1)+'.txt'
        fp = open(filename,'w')
        for docno in finalClusters[clustno]:
            fp.write(listTweets[docno]+"\n")
        fp.close()
    #for ind in order_centroids[i, :10]:
     #   print ' %s' % terms[ind]
        #print
    #plt.figure(1)
    #plt.clf()
    #colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
    #for k, col in zip(range(n_clusters_), colors):
#        my_members = labels == k
#        cluster_center = cluster_centers[k]
#        plt.plot(Xfit[my_members, 0], Xfit[my_members, 1], col + '.')
#        plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
#             markeredgecolor='k', markersize=14)
#    plt.title('Estimated number of clusters: %d' % n_clusters_)
#    plt.show()
#    
    #data = km.cluster_centers_
    #reduced_data = PCA(n_components=2).fit_transform(data)
    #kmeans = KMeans(init='k-means++', n_clusters=true_k, n_init=10)
    #kmeans.fit(reduced_data)
    #print (80 * '=')
    #print data
    #print len(data)
    #print len(data[0])
    #print reduced_data
    #print len(reduced_data)
    #print (80 * '=')

    # Step size of the mesh. Decrease to increase the quality of the VQ.
    #h = 2     # point in the mesh [x_min, m_max]x[y_min, y_max].

    # Plot the decision boundary. For that, we will assign a color to each
    #x_min, x_max = reduced_data[:, 0].min() + 1, reduced_data[:, 0].max() - 1
    #print "::::::::::"
    #print x_min,x_max
    #y_min, y_max = reduced_data[:, 1].min() + 1, reduced_data[:, 1].max() - 1
    #print y_min, y_max
    #xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    #print xx,yy
    #print '....................'
    # Obtain labels for each point in mesh. Use last trained model.
    #Z = km.predict(np.c_[xx.ravel(), yy.ravel()])
    #print Z
    # Put the result into a color plot
    #Z = Z.reshape(xx.shape)
    plt.figure(1)
    plt.clf()
    #plt.imshow(Z, interpolation='nearest',extent=(xx.min(), xx.max(), yy.min(), yy.max()),
           #cmap=plt.cm.Paired,
           #aspect='auto', origin='lower')

    #plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
    # Plot the centroids as a white X
    data = km.cluster_centers_
    centroids = PCA(n_components=2).fit_transform(data)
    #centroids = km.cluster_centers_
    ##print centroids
    plt.scatter(centroids[:, 0], centroids[:, 1],
            marker='x', s=140, linewidths=1,
            color='b', zorder=1)
    plt.title('K-means clustering on the dataset (PCA-reduced data)\n'
          'Centroids are marked with blue cross')
    #plt.xlim(x_min, x_max)
    #plt.ylim(y_min, y_max)
    #plt.xticks(())
    #plt.yticks(())
    plt.show()
    moviedict = {}
    fp = open('movie_dictionary_new.txt','r')
    lines = fp.readlines()
    fp.close()
    for line in lines:
        temp = line.strip("\n")
        temp = temp.split("\t")
        movie = temp[1]
        val = temp[0]
        if movie not in moviedict:
            moviedict[movie] = [val]
        else:
            moviedict[movie].append(val)
    print moviedict.keys()
if __name__ == "__main__":
    print "Calling Main.."
    main() 
