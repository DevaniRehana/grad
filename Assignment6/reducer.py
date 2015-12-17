# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 00:15:00 2015

@author: Harish_kamuju
UTA ID:1001120930
Section : 001 , 6 PM- 8 PM

"""
import sys
import datetime


# input comes from STDIN
wdata = {}

st = datetime.datetime.now()
divider = 0
for line in sys.stdin:
    # remove leading and trailing whitespace
    line = line.strip()
    year,month,day,hour,temp= line.split(' ')
    if temp == '-9999':
        temp = 0
    else:
        temp = int(temp)
    divider += 1
    try:
        wdata[year] = (wdata[year] + temp)/divider
    except:
        wdata[year] = temp
et = datetime.datetime.now()

print "time taken to process:",str(et-st)
for yr in wdata:
    print '%s\t%s'% ( yr, wdata[yr] )
    
