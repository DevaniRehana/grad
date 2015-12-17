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
bucket_name = 'kamuju'
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
                                        Assignment 3 <br>
                                        Environment is Google App Engine</h1>''')
                upload_url = blobstore.create_upload_url('/upload',gs_bucket_name=bucket_name)
            else: 
                upload_url = blobstore.create_upload_url('/upload')
                self.response.out.write('''<h1 style="text-align:center"> Assignment 3 <br>
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
            csvfilekey = ''
            self.response.out.write('''<div align="center"> <h2> In Upload Handler </h2>''')
            
            mydb,tablename = connecttosql()
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
            file_data = self.request.get("upload", default_value=None)
            st = datetime.datetime.now()
            #self.response.out.write(str(file_data))
            if file_data:
                #self.response.out.write('<br>part1<br>')
                filename = self.request.POST["upload"].filename
                #self.response.out.write(filename)
                bf = blob_files.BlobFiles.new(filename,bucket=bucket_name)
                #self.response.out.write('<br>'+str(bf))
                
                if bf:
                    bf.blob_write(file_data)
                    bf.put_async()
                    self.response.out.write('Uploaded and saved in default GCS bucket : ' + bf.gcs_filename)
            et = datetime.datetime.now()
            self.response.out.write('<br>Time taken to upload:'+str(et-st))
            
            try:
                if mydb == None:
                    self.response.out.write('<h3> Unable to connect to DataBase.Please try again later!</h3>')     
                else:
                    cur = mydb.cursor()
                    cur.execute("show tables like '"+tablename+"'")
                    row = cur.fetchone()
                    if not row:
                        self.response.write('<br>Creating the table <br>')
                        createtable = '''CREATE TABLE '''+tablename+''' (time varchar(25) DEFAULT NULL,
                            latitude decimal(15,10) DEFAULT NULL,
                            longitude decimal(15,10) DEFAULT NULL,
                            depth decimal(10,6) DEFAULT NULL,
                            mag decimal(3,2) DEFAULT NULL,
                            magType varchar(5) DEFAULT NULL,
                            nst int(11) DEFAULT NULL ,
                            gap decimal(12,6) DEFAULT NULL,
                            dmin decimal(12,6) DEFAULT NULL,
                            rms decimal(12,6) DEFAULT NULL,
                            net varchar(5) DEFAULT NULL,
                            id varchar(12) NOT NULL,
                            updated varchar(25) DEFAULT NULL,
                            place varchar(100) DEFAULT NULL,
                            type varchar(12) DEFAULT NULL,
                            PRIMARY KEY (id))'''
                        cur.execute(createtable)
                    rows = cur.execute('select * from '+tablename)
                    if rows == 0:
                        self.response.out.write('<br>No records in the table')
                        self.response.out.write('<br>Inserting data from the CSV to table')
                        readers = blobstore.BlobReader(csvfilekey)
                        add_row= '''INSERT INTO '''+tablename+'''(time, latitude, longitude, depth, mag, 
                                magType, nst, gap, dmin, rms, net, id, updated, place,type) values ('%s', %s, %s, %s, %s,'%s', %s, %s, %s, %s,'%s', '%s', '%s', "%s", '%s')'''
                        alldata = csv.reader(readers,delimiter=',')
                        rownum = 1
                        st = datetime.datetime.now()
                        for row in alldata:
                            if rownum == 1:
                                rownum = 0
                                continue
                            row = ['NULL' if x=='' else x for x in row]
                            temp = add_row%tuple(row)
                            try:
                                cur.execute(temp)
                                mydb.commit()
                            except Exception as e:
                                self.response.write('<br>DB Error!!<br>')
                                self.response.write(temp)
                                self.response.write(e.message)
                                self.response.write(str(e.args))
                                continue
                	et = datetime.datetime.now()
                	self.response.out.write('<br>Time taken to insert into DB:'+str(et-st))
                           
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                self.response.write('<br>Exception Occurred!!<br>')
                self.response.write('Line No:'+str(exc_tb.tb_lineno)+'<br>')
                self.response.write(e.message)
                self.response.write(str(e.args))
                mydb.close() 
        mydb.close() 
        self.response.write('</div>')
        self.response.write('</body></html>')
        self.redirect('/myform')
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

class MyRequestHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('''
        <html>
          <body>
          <div align="center"><br><h3>User Query Search </h3>
            <form method="post">
              <p>Magnitude: <input type="number" name="mag" value=0 />.
              <input type="number" name="decimal" value=0 min="0" max="99"></p>
              <p>Location: <input type="text" name="loc" value ="" /></p>
              <p><input type="submit" /></p>
            </form>
            </div>
          </body>
        </html>
        ''')

    def post(self):
        magnitude = self.request.get("mag")
        deci = self.request.get("decimal")
        location = self.request.get("loc")
        mydb,tablename = connecttosql()
        cur = mydb.cursor()
        magni = str(magnitude+'.'+deci)
        qry = 'select * from '+tablename+' where mag='+magni
        if location == "":
            count = cur.execute(qry)
        else:
            qry = qry+' and place like "%'+location+'%"'
            count = cur.execute(qry)
       
        self.response.out.write('''
        <html>
          <body>
          <div align="center"><br><h2>User Query Search Results</h2><br>''')
          
        self.response.out.write('Magnitude:'+magnitude)
        self.response.out.write('<br>')
        self.response.out.write('Location:'+location)
        self.response.out.write('''<br> <h3>Number of Rows fetched:'''+str(count)+'''</h3>''')
        self.response.out.write('''<table border="1" >
  <tr>
    <td>Time</td><td>Latitude</td><td>Longitude</td><td>Depth</td><td>Magnitude</td>
    <td>MagType</td><td>nst</td><td>gap</td><td>dmin</td><td>rms</td>
    <td>net</td><td>id</td><td>updated</td><td>place</td><td>type</td>
  </tr>''')
        for row in cur.fetchall():
            self.response.out.write(
            '''<tr>
            <td>'''+row[0]+'''</td><td>'''+str(row[1])+'''</td><td>'''+str(row[2])+
            '''</td><td>'''+str(row[3])+'''</td><td>'''+str(row[4])+'''</td><td>'''+row[5]+
            '''</td><td>'''+str(row[6])+'''</td><td>'''+str(row[7])+'''</td><td>'''+str(row[8])+
            '''</td><td>'''+str(row[9])+'''</td><td>'''+row[10]+'''</td><td>'''+row[11]+
            '''</td><td>'''+row[12]+'''</td><td>'''+row[13]+'''</td><td>'''+row[14]+
            '''</td>
            </tr>''')
            
        self.response.out.write('''</table></div>
          </body>
        </html>
        ''')

application = webapp2.WSGIApplication([('/', MainPage),
					('/myform', MyRequestHandler),
                                       ('/upload', UploadHandler),                                        
                                       ('/view', ViewHandler),
                                       ('/delete', DeleteHandler)],
                                      debug=True)
