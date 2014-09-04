import urllib2
import scrapeDept
import getopt, sys
from bs4 import BeautifulSoup

def loadCatalog(url):
	page = urllib2.urlopen(url).read()
	soup = BeautifulSoup(page)

	table = soup.find('table', id = 'ctl00_ContentPlaceHolder1_dlSubjects')

	urls = []

	for anchor in table.findAll('a', href=True):
	    if anchor.get('href') != "#":
	    	
	    	toAdd = "http://catalog.oregonstate.edu/"+anchor.get('href')+"&columns=afjk"
	    	urls.append(toAdd)

	#print urls
	
	for i in range(0, len(urls)):
		scrapeDept.getData(urls[i])


def main():
	#example url: http://catalog.oregonstate.edu/SOC.aspx?level=all&campus=corvallis&term=201500
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'u:', [ 'url='])
	except getopt.GetoptError as err:
		# print help information and exit:
		print(err) # will print something like "option -a not recognized"
		#usage()
		sys.exit(2)
	for o, a in opts:

		if o in ( '-u', '--url'):
			url = a
			loadCatalog(url)
		else:
			assert False, "unhandled option"

if __name__ == "__main__":
    main()
    