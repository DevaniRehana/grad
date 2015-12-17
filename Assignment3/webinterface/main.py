#Author Harish Kamuju
#UTA ID : 1001120930
#Section : 003 (6:00PM to 8:00PM)
#Assignment : 3

import jinja2
import csv
import os,sys
import webapp2
import datetime,time
import blob_files
import cloudstorage as gcs
import MySQLdb
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext.webapp import blobstore_handlers

my_default_retry_params = gcs.RetryParams(initial_delay=0.2,
                                          max_delay=5.0,
                                          backoff_factor=2,
                                          max_retry_period=15)
gcs.set_default_retry_params(my_default_retry_params)
bucket_name = 'kamujuh'
env = os.getenv('SERVER_SOFTWARE')

#template loader for html files 
template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getcwd()))

#creates a db like model to process multiple user data
class UserUpload(db.Model):
    user = db.UserProperty()
    description = db.StringProperty()
    timetaken = db.StringProperty()
    blob = blobstore.BlobReferenceProperty()

#Main page handler for uploads
class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
       	    greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %(user.nickname(), users.create_logout_url('/')))
	else:
	    greeting = ('<a href="%s">Sign in or register</a>.' %users.create_login_url('/'))
	
        self.response.out.write('<html><body>%s</body></html>' % greeting)
        #login_url = users.create_login_url(self.request.path)
        #logout_url = users.create_logout_url(self.request.path)
    
        uploads = None
        if user:
            q = UserUpload.all()
            q.filter('user =', user)
            q.ancestor(db.Key.from_path('UserUploadGroup', user.email()))
            uploads = q.fetch(100)
        try:
            if (env and env.startswith('Google App Engine/')):
                # Connecting from App Engine
                self.response.out.write('''<h1 style="text-align:center"> 
                                        Assignment 7 <br>
                                        Environment is Google App Engine</h1>''')
                upload_url = blobstore.create_upload_url('/upload',gs_bucket_name=bucket_name)
            else: 
                upload_url = blobstore.create_upload_url('/upload')
                self.response.out.write('''<h1 style="text-align:center"> Assignment 7 <br>
                                    Environment is Local DEV</h1>''')
        
            self.response.out.write('''<h2 style="text-align:center"> Uploads images</h2>''')
     
            template = template_env.get_template('home.html')
            context = {
                'user': user,
                'login_url': login_url,
                'logout_url': logout_url,
                'uploads': uploads,
                'upload_url': upload_url,
                }
        
            self.response.write(template.render(context))
        except Exception as e:
            self.response.write('Exception Occurred!!<br>')
            self.response.write(e.message)
            self.response.write(str(e.args))
#Upload handler to write files to cloud storage and blob storage.  
def connecttosql():
    #Functionality to connect to the database.
    if (env and env.startswith('Google App Engine/')):
        mydb = MySQLdb.connect(
            unix_socket='/cloudsql/wide-plating-97021:cloudkamuju',
            db='testdb',user='root',passwd='mypassword@123')
        tablename = 'finalcloud'
    else:
         # Connecting from local network.
         # Make sure your network is whitelisted
        mydb = MySQLdb.connect(host='127.0.0.1',port=3306,db='cloud',
                user='root',passwd='password')
        tablename = 'localcloud'
    return mydb,tablename
    
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            self.response.out.write('''<div align="center"> <h2> In Upload Handler </h2>''')
            
            mydb,tablename = connecttosql()
            user = users.get_current_user()
            description = self.request.params['description']
         
            for blob_info in self.get_uploads('upload'):
                file_name = blobstore.BlobInfo.get(blob_info.key()).filename
                ext = [".jpg",".jpeg",".gif",".png",".JPG",".JPEG"]
                if not file_name.endswith(tuple(ext)):
                    continue
                csvfilekey = blob_info.key()
                upload = UserUpload(
                    parent=db.Key.from_path('UserUploadGroup', user.email()),
                    user=user,
                    description=description,
                    blob=blob_info.key())
                upload.put()
                
        except Exception as e:
            self.response.write('<br>Exception Occurred!<br>')
            self.response.write(e.message)
            self.response.write(str(e.args))
    	self.redirect('/')    
def get_upload(key_str, user):
    user = users.get_current_user()
    upload = None
    if key_str:
        upload = db.get(key_str)

    if (not user or not upload or upload.user != user):
        return None
    return upload

class ViewHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        upload = get_upload(self.request.params.get('key'),
                            users.get_current_user())
        if not upload:
            self.error(404)
            return
        self.send_blob(upload.blob)
        

class DeleteHandler(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            entities_to_delete = []
            blobs_to_delete = []
            for delete_key in self.request.params.getall('delete'):
                upload = db.get(delete_key)
                if upload.user != user:
                    continue
                entities_to_delete.append(upload.key())
                blobs_to_delete.append(upload.blob.key())

            db.delete(entities_to_delete)
            blobstore.delete(blobs_to_delete)

        self.redirect('/')


application = webapp2.WSGIApplication([('/', MainPage),
                                       ('/upload', UploadHandler),                                        
                                       ('/view', ViewHandler),
                                       ('/delete', DeleteHandler)],
                                      debug=True)
