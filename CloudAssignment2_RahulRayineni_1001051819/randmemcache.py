#Rahul Rayineni
#1001051819
#cloud computing assignment2
#program to calculate time for 2000 random queries using memcache
import time
import sys
import MySQLdb
import random
try:
    conn = MySQLdb.connect ("cloud.cqttge96yqpa.us-west-2.rds.amazonaws.com",
                            "root",
                            "clouduta",
                            "clouduta")
except MySQLdb.Error, e:
        print e
        sys.exit(1)
cursor = conn.cursor()
starttime=time.time()
c=1
while c<=2000:
    rand = random.randint(1, 30)
    print rand
    c += 1
    cursor.execute("SELECT latitude,longitude,mag FROM all_month where nst='%d'" %rand)
    print "Query Exceured",c
print ("time taken to execute 2000 random queries",time.time()-starttime)

