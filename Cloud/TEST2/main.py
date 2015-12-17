import jinja2
import csv
import os,sys
import webapp2
#import logging
import datetime
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
bucket_name = 'kamuju'
env = os.getenv('SERVER_SOFTWARE')

template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getcwd()))

class UserUpload(db.Model):
    user = db.UserProperty()
    description = db.StringProperty()
    timetaken = db.StringProperty()
    blob = blobstore.BlobReferenceProperty()

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        login_url = users.create_login_url(self.request.path)
        logout_url = users.create_logout_url(self.request.path)
    
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
                                        Test 2 <br>
                                        Environment is Google App Engine</h1>''')
                upload_url = blobstore.create_upload_url('/upload',gs_bucket_name=bucket_name)
            else: 
                upload_url = blobstore.create_upload_url('/upload')
                self.response.out.write('''<h1 style="text-align:center"> Test 2 <br>
                                    Environment is Local DEV</h1>''')
        
            self.response.out.write('''<h2 style="text-align:center"> Uploads only csv files</h2>''')
     
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
        
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            csvfilekey = ''
            self.response.out.write('''<div align="center"> <h2> In Files Handler </h2>''')
            if (env and env.startswith('Google App Engine/')):
                mydb = MySQLdb.connect(
                    unix_socket='/cloudsql/wide-plating-97021:cloudkamuju',
                    db='testdb',user='root',passwd='mypassword@123')
                tablename = 'test2cloud'
            else:
                 # Connecting from local network.
                 # Make sure your network is whitelisted
                mydb = MySQLdb.connect(host='127.0.0.1',port=3306,db='cloud',
                        user='root',passwd='password')
                tablename = 'local2cloud'
                
            user = users.get_current_user()
            description = self.request.params['description']
           
            for blob_info in self.get_uploads('upload'):
                file_name = blobstore.BlobInfo.get(blob_info.key()).filename
                if not file_name.endswith('.csv'):
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
        
        if csvfilekey == '':
            self.response.out.write('Please upload correct csv to display Earthquake Data<br>')
        else:
            #Connect to Cloud SQL and insert the queries.
            self.response.write(str(datetime.datetime.now()))
            file_data = self.request.get("upload", default_value=None)
            st = datetime.datetime.now()
            self.response.out.write(str(file_data))
            if file_data:
                self.response.out.write('<br>part1<br>')
                filename = self.request.POST["upload"].filename
                self.response.out.write(filename)
                bf = blob_files.BlobFiles.new(filename,bucket=bucket_name)
                self.response.out.write('<br>'+str(bf))
                
                if bf:
                    bf.blob_write(file_data)
                    bf.put_async()
                    self.response.out.write('Uploaded and saved in default GCS bucket : ' + bf.gcs_filename)
            et = datetime.datetime.now()
            self.response.out.write('<br>Time taken to upload:'+str(et-st))
            self.response.out.write('<br> List of files in the bucket:<br>')
            for gcs_filename, filename in blob_files.BlobFiles.list_gcs_file_names(bucket=bucket_name,folder='/upload'):
                self.response.out.write('<br>'+gcs_filename+'<br>')
            
            try:
                if mydb == None:
                    self.response.out.write('<h3> Unable to connect to DataBase.Please try again later!</h3>')     
                else:
                    count = 0
                    cur = mydb.cursor()
                    rows = cur.execute('select * from '+tablename)
                    readers = blobstore.BlobReader(csvfilekey)
                    alldata = csv.reader(readers,delimiter=',')
                    rownum = 1
		    for row in alldata:
		    	if rownum == 1:
		            rownum = 0
		            continue
                        if '2' in row[3]:
                        	count +=1
                    self.response.write('No of tuples =:',str(count))

                    self.response.out.write('<br><h3>Weekwise Storm Data</h3></div>')
                    for magval in ['=2','=3','=4','>=5']:
                        selectqry = 'select week(time),count(*)  from '+tablename+' where mag '+magval+' group by week(time)'
                        cur.execute(selectqry)
                        rows = cur.fetchall()
                        #temp = '''<br><table> <tr><th colspan="6">For Magnitude'''+magval+'''</th>
                         #</tr> <tr><td>Week</td><td>Count</td></tr><tr>'''
                        self.response.out.write('<div align="center"><table border="1" width="300"  style="float: left;"> <tr><th colspan="6">For Magnitude')
                        self.response.out.write(str(magval)+'</th></tr> <tr><td>Week</td><td>Count</td></tr><tr>')
                        for row in rows:
                            temp = "<td>"+str(row[0])+"</td><td>"+str(row[1])+"</td></tr>"
                            self.response.out.write(temp)
                        self.response.out.write('</table>')
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                self.response.write('<br>Exception Occurred!!<br>')
                self.response.write('Line No:'+str(exc_tb.tb_lineno)+'<br>')
                self.response.write(e.message)
                self.response.write(str(e.args))
        self.response.write('</div>')
        self.response.write('</body></html>')
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
