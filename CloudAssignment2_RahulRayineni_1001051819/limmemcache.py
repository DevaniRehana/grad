

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
cursor = conn.cursor()
c=1
starttime=time.time()
while c<=500:
        c += 1
        rand = random.randint(1, 30)
        popularfilms = memc.get('example')
        if not popularfilms:
            cursor.execute("SELECT mnth, Count(weekday) ,count(workingday) FROM day group by mnth")
            results = cursor.fetchall()
            for row in results:
                print "month", row[0], "count(weekday)", row[1],"count(working day", row[2] 
            memc.set('example',rows,60)
        else:
            for row in popularfilms:
                print "month", row[0], "count(weekday)", row[1],"count(working day", row[2] 
print ("time taken to execute 2000 random queries",time.time()-starttime)
