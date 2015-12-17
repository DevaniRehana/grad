
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
while c<=500:
    c += 1
    cursor.execute("SELECT mnth, Count(weekday) ,count(workingday) FROM day group by mnth")
    results = cursor.fetchall()
    for row in results:
        print "month", row[0], "count(weekday)", row[1],"count(working day", row[2] 
print ("time taken to execute 2000 random queries",time.time()-starttime)

