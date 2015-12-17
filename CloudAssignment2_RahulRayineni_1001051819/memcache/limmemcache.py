#Rahul Rayineni
#1001051819
#cloud computing assignment2
#program to calculate time for limted scope using memcache

import time
import sys
import MySQLdb
import memcache
memc = memcache.Client(['127.0.0.1:11211'], debug=1);
try:
    conn = MySQLdb.connect ("cloud.cqttge96yqpa.us-west-2.rds.amazonaws.com",
                            "root",
                            "clouduta",
                            "clouduta")
except MySQLdb.Error, e:
        print e
        sys.exit (1)
starttime=time.time()
c=1
while c<=2000:
        c += 1
        popularfilms = memc.get('example')
        if not popularfilms:
                cursor = conn.cursor()

                cursor.execute('SELECT latitude,logitude,mag FROM (select * from all_month limit 2000) as Scope ORDER BY RAND() LIMIT 1')
                rows = cursor.fetchall()
                memc.set('example',rows,60)
                print "Updated memcached with MySQL data"
        else:
                print "Loaded data from memcached"
print ("time taken to execute 2000 random queries",time.time()-starttime)
