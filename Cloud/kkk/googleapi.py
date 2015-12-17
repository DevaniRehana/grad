__author__ = 'kaushika'
import logging
import os
import cloudstorage as gcs
import webapp2
import MySQLdb

from google.appengine.api import app_identity

# Retry can help overcome transient urlfetch or GCS issues, such as timeouts.
my_default_retry_params = gcs.RetryParams(initial_delay=0.2,
                                          max_delay=5.0,
                                          backoff_factor=2,
                                          max_retry_period=15)

gcs.set_default_retry_params(my_default_retry_params)


class MainPage(webapp2.RequestHandler):
  """Main page for GCS demo application."""

def get(self):

    bucket_name = 'kaushikabucket'

    bucket = '/' + 'kaushikabucket'
    filename = bucket + '/all_month.csv'
    self.tmp_filenames_to_clean_up = []

  if(inputValue=='1'):
      self.read_file(filename)
      self.response.write('\n\n')
  elif(inputValue == '2'):
      self.Queryresult_set()
  #else:
      #self.response.write("enter coreect optin")
def read_file(self,filename):
    self.response.write("file content")
     env = os.getenv('SERVER_SOFTWARE')
        if (env and env.startswith('Google App Engine/')):
            # Connecting from App Engine
            db = MySQLdb.connect(
             unix_socket='/cloudsql/firstproject-971:cloudsecond',
            user='root')
        else:
            # Connecting from an external network.
            # Make sure your network is whitelisted
            db = MySQLdb.connect(host='173.194.87.179',port=3306,user='root',passwd='root')
    cursor = db.cursor()
        gcs_file = gcs.open(filename)
        data=csv.reader(gcs_file)
     for x in data:
        cursor.execute('DROP TABLE IF EXISTS test_csv11')
        cursor.execute('create table test_csv11(time varchar(80),latitude varchar(80),longitude varchar(80),depth varchar(80),mag varchar(80),magType varchar(80),nst varchar(80),gap varchar(80),dmin varchar(80),rms varchar(80),net varchar(80),id varchar(80),updated varchar(80),place varchar(80),type varchar(80));')

        fields=cursor.fetchall()




app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)