import MySQLdb
import sys
import unicodedata
import personalInfo as PI
import urllib2
import datetime
from bs4 import BeautifulSoup
import re

def getData(url):

	#connect to MySQL database
	db = connect(PI)

	#page will eventually be loaded through loop on original page.
	#page = urllib2.urlopen('http://catalog.oregonstate.edu/SOCList.aspx?subjectcode=PAX&termcode=201500&campus=corvallis&columns=afjk').read()
	
	print url

	page = urllib2.urlopen(url).read()
	allClassArray = []

	soup = BeautifulSoup(page)
	#soup.prettify()

	#find the table that contains all courses
	table = soup.find('table', id="ctl00_ContentPlaceHolder1_dlCourses")

	#Will use i to get the correct title
	i = 0

	#find the tables for each course
	for table2 in table.findAll('table', id = re.compile("gvOfferings")):

		courseID = table.findAll('h5')
		
		#find all rows, skipping the header row
		for row in table2.findAll('tr')[1:]:    

			j = 0

			Array = []

			Array.append(courseID[i].text.strip())

			for cell in row.findAll('td'):

				if j == 3:
					stringtosplit = cell.text
					
					try:
						
						#Prepare the Day/Time/Date column for database entry
						#Note there is a special case when a class meets different times
						#Different days of the week.  Currently this only handles if there are two
						#Different times. Don't think there are any with ore.
											
						datelist = re.split('-| |<br>',stringtosplit.strip())	
																
						if len(datelist) >=	3:			
							lines = []
							text = cell.findAll('font')
							
							for string in text[0].stripped_strings:
								#line = repr(string)
								#line = str(line)
								#print line
										
								line = re.split('-| |<br>',string.strip())			
								lines.append(line)
					
							n = 0
							datelist = []
							datelists = []
							for line in lines:
								#line contains day of week, times
								if n%2 == 0:
									datelist = []
									days = line[0]
									starttime = line[1]
									endtime = line[2]
									datelist.append(days)
									datelist.append(starttime)
									datelist.append(endtime)
								
								#line contains dates
								else:
									#if only a start date, then use for start and end date
									if len(line) == 1:
										startdate = line[0]
										enddate = line[0]
									elif len(line) == 2:
										startdate = line[0]
										startdate.encode('utf-8')
										enddate = line[1]
										
									datelist.append(startdate)
									datelist.append(enddate)
									datelists.append(datelist)
								
									
								n=n+1
							Array.append(datelists)											
							
						else:
							Array.append(cell.text.strip())


					#if the index error occurs, it means the cell wasn't the date/time.
					except IndexError:
						Array.append(cell.text.strip())

				else:
					Array.append(cell.text.strip())

				j = j + 1

			#print Array
			allClassArray.append(Array)
			
			#Add instructor to database if instructor is not Staff. Doesn't matter for schedule, 
			#if don't know who the person is.
			curInstructor = Array[3]
			
			if curInstructor != 'Staff':
				instructor = addInstructor(db, Array[3])
				instructor_id = instructor[0]
				
				#add course to database if time is not TBA
								
				if Array[4][:3] != 'TBA':
					
					for n in range (0, len(Array[4])):
						
						print Array[4]
						
						#escape things like quotes in course titles
						title = re.escape(Array[0])
						
						
						crn = Array[2]	
						start_date = datetime.datetime.strptime(Array[4][n][3], "%m/%d/%y").date()
						end_date = datetime.datetime.strptime(Array[4][n][4], "%m/%d/%y").date()
						days_of_week = Array[4][n][0]
						start_time = Array[4][n][1]
						end_time = Array[4][n][2]
					
						#Add course to course database
						course = addCourse(db, instructor_id, crn, title, start_date, end_date, days_of_week, start_time, end_time)
						
						course_id = course[0]	
						getMeetings(start_date, end_date, days_of_week, crn, course_id)
										
					

		#increment to get the next title
		i = i + 1
	db.close()

		

#Function that gets all the meeting dates for an individual course, by CRN
def getMeetings(startDate, endDate, daysOfWeek, CRN, course_id):
	
	db = connect(PI)
	startDayOfWeek = startDate.weekday()

	#Get days of week a class is meeting, convert to integers
	meetingDays = list(daysOfWeek)

	for i in range(0, len(meetingDays)):
		#print i
		if meetingDays[i] == "U":
			meetingDays[i]=6
		if meetingDays[i] == "M":
			meetingDays[i]=0
		elif meetingDays[i] == "T":
			meetingDays[i]=1
		elif meetingDays[i] == "W":
			meetingDays[i]=2
		elif meetingDays[i] == "R":
			meetingDays[i]=3
		elif meetingDays[i] == "F":
			meetingDays[i]=4
		elif meetingDays[i] == "S":
			meetingDays[i]=5

	#print meetingDays
	#print startDayOfWeek

	curDate = startDate

	dateRange = (endDate - startDate).days

	#Check all dates including the final date of the date range
	for i in range (0, dateRange+1):
		for j in range (0, len(meetingDays)):
			if meetingDays[j] == curDate.weekday():
				#print str(CRN)+' '+str(curDate)
				addMeetings(db, CRN, curDate, course_id)
		curDate += datetime.timedelta(days=1)
		
	db.close()
		

def connect(info):
	db = MySQLdb.connect(host=info.myHost(), user=info.myUsername(), passwd=info.myPassword(), db=info.myDB())
	return db
	
def addInstructor(db, directory_name):
	cursor = db.cursor()
	#INSERT IGNORE only inserts if not in database
	cursor.execute("INSERT IGNORE into Users (directory_name) values ('%s')" % (re.escape(directory_name)))
	cursor.execute("SELECT user_id FROM Users WHERE directory_name = ('%s')" % (re.escape(directory_name)))
	row = cursor.fetchone() 
	db.commit()
	cursor.close()
	return row
	
def addCourse(db, instructor_id, crn, title, start_date, end_date, days_of_week, start_time, end_time):
	
	'''print instructor_id
	print crn
	print start_date
	print end_date
	print days_of_week
	print start_time
	print end_time'''
	
	cursor = db.cursor()
	cursor.execute('''INSERT IGNORE into Courses (instructor_id, crn, title, start_date, 
	end_date, days_of_week, start_time, end_time) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
	''' % (instructor_id, crn, title, start_date, end_date, days_of_week, start_time, end_time))
	cursor.execute("SELECT course_id FROM Courses WHERE (instructor_id='%s' AND crn='%s' AND start_date= '%s' AND days_of_week='%s' AND start_time='%s' AND end_time='%s')" % (instructor_id, crn, start_date, days_of_week, start_time, end_time))
	row = cursor.fetchone()
	db.commit()
	cursor.close()
	return row
	
def addMeetings(db, crn, date, course_id):
	cursor = db.cursor()
	cursor.execute("INSERT IGNORE into CourseMeetings (crn, course_id, date) values ('%s', '%s', '%s')" % (crn, course_id, date))
	cursor.close()
	db.commit()

def main():
	getData("http://catalog.oregonstate.edu/SOCList.aspx?termcode=201501&campus=corvallis&level=all&subjectcode=PSY&columns=afjk")

if __name__ == "__main__":
    main()
    


