
#import pandas as pd

import datetime,sys
def read_input(file):
    for line in file:
        # split the line
        yield line.split(',')
data = read_input(sys.stdin)
for line in data:
    print line
        #if prosub.find(str(row[7])) or year.find(str(row[1])) or state.find(str(row[23])):
#df = pd.read_csv('30yr_03945.dat',header=None, delim_whitespace=True)
#df.columns = ['year','month','day','hour','Airtemp','DewPointTemp',
#                'SeaLevelPressure','WindDirection','WindSpeedRate',
#                'SkyCondition','L1','L2']
#for index, row in df.iterrows():
    #print '%s\t%s\t%s\t%s\t%s' %(row['year'],row['month'],row['day'],row['hour'],row['Airtemp'])
#    print row['year'],row['month'],row['day'],row['hour'],row['Airtemp']
