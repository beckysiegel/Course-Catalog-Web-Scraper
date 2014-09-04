import csv
import MySQLdb
import sys
import personalInfo as PI
	
	
def connect(info):
	db = MySQLdb.connect(host=info.myHost(), user=info.myUsername(), passwd=info.myPassword(), db=info.myDB())
	return db

def addEmail(db, mycsv):
	cursor = db.cursor()
	
	csv_data = csv.reader(file(mycsv))
	for row in csv_data:	
		try:
			cursor.execute("UPDATE Users SET osu_username ='%s', gcal_email='%s', gcal_pw='%s' WHERE directory_name = '%s'" % (row[0], row[1], row[2], row[3]))
		except IndexError:
			cursor.execute("INSERT IGNORE into Users (osu_username, gcal_email, gcal_pw, directory_name)  values ('%s', '%s', '%s', null)" % (row[0], row[1], row[2]))
	
	#close the connection to the database.
	db.commit()
	cursor.close()
	print "Done"

def main():
	db = connect(PI)
	addEmail(db, 'data.csv')
	db.close()

if __name__ == "__main__":
    main()
    