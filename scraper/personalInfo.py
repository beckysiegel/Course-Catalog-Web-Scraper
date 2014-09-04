#!/usr/bin/python
import MySQLdb

#database information removed for privacy!

def myHost():
	return 'xxxx'
def myUsername():
	return 'xxxx'
def myDB():
	return 'xxxx'
def myPassword():
	return 'xxxx'

def connect():
	db = MySQLdb.connect(host=myHost(), user=myUsername(), passwd=myPassword(), db=myDB())
	return db
