# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 00:15:00 2015

@author: Harish_kamuju
UTA ID:1001120930
Section : 001 , 6 PM- 8 PM

"""

from org.apache.hadoop.fs import Path
from org.apache.hadoop.io import *
from org.apache.hadoop.mapred import *

import pandas as pd
import numpy as np
import datetime

import sys
import getopt

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
 

class WeatherMap(Mapper, MapReduceBase):
    one = IntWritable(1)
    def map(self, key, value, output, reporter):
        for w in value.toString().split():
            output.collect(Text(w), self.one)
class Summer(Reducer, MapReduceBase):
    def reduce(self, key, values, output, reporter):
        sum = 0
        while values.hasNext():
            sum += values.next().get()
        output.collect(key, IntWritable(sum))
def printUsage(code):
    print "weather [-m <maps>] [-r <reduces>] <input> <output>"
    sys.exit(code)
    
def main(args):
    conf = JobConf(WeatherMap);
    conf.setJobName("weatheranalysis");
    conf.setOutputKeyClass(Text);
    conf.setOutputValueClass(IntWritable);
    conf.setMapperClass(WordCountMap);
    conf.setCombinerClass(Summer);
    conf.setReducerClass(Summer);
    try:
        flags, other_args = getopt.getopt(args[1:], "m:r:")
    except getopt.GetoptError:
        printUsage(1)
    if len(other_args) != 2:
        printUsage(1)
    for f,v in flags:
        if f == "-m":
            conf.setNumMapTasks(int(v))
        elif f == "-r":
            conf.setNumReduceTasks(int(v))
    conf.setInputPath(Path(other_args[0]))
    conf.setOutputPath(Path(other_args[1]))
    JobClient.runJob(conf);
    
if __name__ == "__main__":
    main(sys.argv)