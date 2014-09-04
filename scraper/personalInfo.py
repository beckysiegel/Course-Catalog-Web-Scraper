#!/usr/bin/python
import MySQLdb

def myHost():
	return 'mysql.cs.orst.edu'
def myUsername():
	return 'cs419_group9'
def myDB():
	return 'cs419_group9'
def myPassword():
	return 'dZmXnT5MydhwddA2'

def connect():
	db = MySQLdb.connect(host=myHost(), user=myUsername(), passwd=myPassword(), db=myDB())
	return db