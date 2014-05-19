from icalendar import Calendar, Event
import datetime
import string
import sys
import argparse
import csv
import dateutil.parser
import time
import pytz


def startCalendar(calId, version):
	cal = Calendar()
	cal.add('prodid', calId)
	cal.add('version', version)
	return cal

def generateUuid(month, day, name):
	moddedName = string.upper(string.replace(name, " ", ""))
	return "BDAY-%s-%s-%s" % ("{0:02d}".format(month), "{0:02d}".format(day), moddedName)

def decorateEvent(event, month):
	event.add('CATEGORIES', 'Birthdays')
	event.add('CLASS', 'PRIVATE')
	event.add('TRANSP', 'TRANSPARENT')
	event.add('RRULE:FREQ=YEARLY;BYMONTH=%s' % (month),"")

def addEvent(cal, name, parsedDate):
	currentYear = int(time.strftime("%Y"))
	dateMonth = parsedDate.month
	dateDay = parsedDate.day
	startDate = datetime.date(currentYear, dateMonth, dateDay)
	eventName = "%s%s" % (name, "'s Birthday")
	event = Event()
	decorateEvent(event, dateMonth)
	event.add('summary', eventName)
	event.add('dtstart', startDate)
	event.add('dtstamp', datetime.datetime.now())
	event.add('UID', generateUuid(dateMonth, dateDay, name))
	event.add('DESCRIPTION', parsedDate)
	cal.add_component(event)

def main(outputFile, birthdayFile, nameColumn, dateColumn, delimiter):	
	print "Converting birthday CSV to iCal file with params (namecolumn:%s, datecolumn:%s, delimiter:%s)" % (nameColumn, dateColumn, delimiter)
	fileHandle = open(birthdayFile, "r")
	birthdayReader = csv.reader(fileHandle, delimiter=delimiter)
	cal = startCalendar('BirthdayCalendar', '2.0')
	for row in birthdayReader:
		name = string.strip(row[nameColumn])
		date = string.strip(row[dateColumn])
		if not name or not date:
			print "Skipping line %s" % (', '.join(row))
			continue
		parsedDate = None
		try:
			parsedDate = dateutil.parser.parse(date)
		except (TypeError, ValueError) as e:
			print "Error parsing date %s" % (date)
		if not parsedDate:
			print "Skipping line %s" % (', '.join(row))
			continue
		addEvent(cal, name, parsedDate)
		print "Successfully added %s %s" % (name, date)
	fileHandle.close()
	outputFileHandle = open(outputFile, 'wb')
	outputFileHandle.write(cal.to_ical())
	outputFileHandle.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--birthdayfile', required=True)
    parser.add_argument('-o', '--outputfile', required=True)
    parser.add_argument('-n', '--namecolumn', required=False, default=0,  help='The column with names, 0 indexed (default: 0)', type=int)
    parser.add_argument('-d', '--datecolumn', required=False,  default=1, help='The column with dates, 0 indexed (default: 1)', type=int)
    parser.add_argument('-D', '--delimiter', required=False,  default=",", help='The delimiter (default: ,)')
    args = vars(parser.parse_args(sys.argv[1:]))
    main(args['outputfile'], args['birthdayfile'], args['namecolumn'], args['datecolumn'], args['delimiter'])