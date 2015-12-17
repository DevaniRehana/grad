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
cursor.execute("DROP VIEW IF EXISTS Scope")
cursor.execute("create view Scope as select * from all_month limit 2000")
starttime=time.time()
while c<=2000:
        c += 1
        rand = random.randint(1, 30)
        popularfilms = memc.get('example')
        if not popularfilms:
            cursor.execute("SELECT latitude,longitude,mag FROM Scope where nst='%d'" %rand)
            rows = cursor.fetchall()
            memc.set('example',rows,60)
            print "Query executed",c
        else:
            print "Query executed",c
print ("time taken to execute 2000 random queries",time.time()-starttime)

