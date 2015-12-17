import os
import MySQLdb
import csv,logging,sys
from google.appengine.ext.webapp.util import run_wsgi_app
import cloudstorage as gcs
import cgi
import webapp2
import jinja2

my_default_retry_params = gcs.RetryParams(initial_delay=0.2,
                                          max_delay=5.0,
                                          backoff_factor=2,
                                          max_retry_period=15)
gcs.set_default_retry_params(my_default_retry_params)
_INSTANCE_NAME = 'save-980:save'
JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  autoescape=True,
  extensions=['jinja2.ext.autoescape'])

class GoogleAppEngine(webapp2.RequestHandler):
    def get(self):
    	self.response.out.write('In Get')
    #def post(self):
        bucket_name = 'kaushikabucket'
        bucket = '/' + bucket_name
        filename = bucket + '/all_month.csv'
        self.tmp_filenames_to_clean_up = []

        self.read_file(filename)
        self.response.write('\n\n')

        self.Queryresult_set()

    def read_file(self, filename):
        self.response.write('file content:<br>')
        #self.responce.write(filename+'\n')
        env = os.getenv('SERVER_SOFTWARE')
        if (env and env.startswith('Google App Engine/')):
            # Connecting from App Engine
            db = MySQLdb.connect(unix_socket='/cloudsql/firstproject-971:cloudsecond',user='root',db='cloud_secondproject')
        else:

            db = MySQLdb.connect(host='173.194.87.179',port=3306,user='kaushika',passwd='password',db='cloud_secondproject')
        cursor = db.cursor()
            # Alternatively, connect to a Google Cloud SQL instance using:
            # db = MySQLdb.connect(host='ip-address-of-google-cloud-sql-instance', port=3306, db='guestbook', user='root', charset='utf 8')
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
       # if gcs_file_exists(filename):
       #     self.response.write('File exists')
       # else:
       #     self.response.write('No')
       #     sys.exit(0)
        logging.info('file %s',filename)
        
        gcs_file = gcs.open(filename)
        
        #gcs_file = gcs.open(filename)
        #lines=gcs_file.readlines()
        #self.response.write(lines)
        
        cursor.execute('DROP TABLE IF EXISTS test_csv11')
        cursor.execute('create table test_csv11(time varchar(80),latitude varchar(80),longitude varchar(80),depth varchar(80),mag varchar(80),magType varchar(80),nst varchar(80),gap varchar(80),dmin varchar(80),rms varchar(80),net varchar(80),id varchar(80),updated varchar(80),place varchar(80),type varchar(80));')
	
        data = csv.reader(gcs_file)
        self.response.out.write(str(data)+'ddddd<br>')
	
        for x in data:
            cursor.execute('INSERT INTO main (time, latitude, longitude, depth, mag, magType, nst, gap, dmin, rms, net, id, updated, place,type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8],x[9],x[10],x[11],x[12],x[13],x[14])) 
            
            db.commit()
            db.close()
    def Queryresult_set(self):
        env = os.getenv('SERVER_SOFTWARE')
        if (env and env.startswith('Google App Engine/')):
            # Connecting from App Engine
            db = MySQLdb.connect(unix_socket='/cloudsql/firstproject-971:cloudsecond',user='root')
        else:
            # Connecting from an external network.
            # Make sure your network is whitelisted
            db = MySQLdb.connect(host='173.194.87.179',port=3306,user='root',passwd='root')

            # db = MySQLdb.connect(host='ip-address-of-google-cloud-sql-instance', port=3306, db='guestbook', user='root', charset='utf 8')
        cursor = db.cursor()
        cursor.execute("select week(time), count(*) from testcsv11 where mag=2 group by week(time)")
        #fields=cursor.fetchall()
        whether = [];
        for row in cursor.fetchall():
          whether.append(dict([('week',cgi.escape(row[0])),
                                 ('count',cgi.escape(row[1])),

                                 ]))

        variables = {'whether': whether}
        template = JINJA_ENVIRONMENT.get_template('appengine.html')
        self.response.write(template.render(variables))
        db.commit()
        db.close()

        self.redirect("/")

application = webapp2.WSGIApplication([('/', GoogleAppEngine),
                               ],
                              debug=True)

def main():
    application = webapp2.WSGIApplication([('/',GoogleAppEngine),
                                           ],
                                          debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()