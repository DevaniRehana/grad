# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 00:15:00 2015

@author: Home
"""

import pandas as pd
import numpy as np
import datetime
def mapper():
    months = range(1,13)
    hours = range(0,25)
    df = pd.read_csv('30yr_03945.dat',header=None, delim_whitespace=True)
    df.columns = ['year','month','day','hour','Airtemp','DewPointTemp',
                'SeaLevelPressure','WindDirection','WindSpeedRate',
                'SkyCondition','L1','L2']
    return df
    #Setting default values to -9999 
def reducer(df):
    st = datetime.datetime.now()
    df.loc[df['Airtemp'] == -9999] = 0
    
    #df.loc[df['hour']] = df.loc[df['hour']]/10
    groupyear = df.groupby(['year','month']).mean()
    #groupyear = df.groupby(['year','month']).mean()
    #fi = groupyear['Airtemp']
    #fi.plot()
    fi = groupyear['SeaLevelPressure']
    fi.plot()
    et = datetime.datetime.now()
    print 'Time taken for analysis' +str(et-st)
if __name__ == "__main__":
    df = mapper()
    reducer(df)