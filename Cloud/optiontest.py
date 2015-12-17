# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 15:13:37 2015

@author: Home
"""
def put():
    print "in put"
    
def get():
    print "in get"
def listobj():
    print "in listobj"
def deleteobj():
    print "in del"

options = {'1':put,'2':get,'3':listobj,'4':deleteobj}
inp = raw_input("Select any of the options from the menu.\n1:put\n2:get\n3:list\n4:del\n->")

options[inp]()