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
cursor.execute("DROP VIEW IF EXISTS Scope")
cursor.execute("create view Scope as select * from all_month limit 2000")
starttime=time.time()
c=1
while c<=2000:
    rand = random.randint(1, 30)
    print rand
    c += 1
    cursor.execute("SELECT latitude,longitude,mag FROM Scope where nst='%d'" %rand)
    print "Query Exceured",c
print ("time taken to execute 2000 random queries",time.time()-starttime)

