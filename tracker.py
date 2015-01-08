"""

This is a simple task-tracker that saves data into a pre-specified csv location.

"""

# import dependencies
from datetime import date, timedelta as td
import datetime
import time as now
import pandas
import csv
import sqlite3 as dbapi
2

#Define Timer Object
class Timer(object):
    """A simple timer class"""

    def __init__(self):
        pass

    def start(self):
        """Starts the timer"""
        self.start = datetime.datetime.now()
        return self.start

    def stop(self, message="Total: "):
        """Stops the timer.  Returns the time elapsed"""
        self.stop = datetime.datetime.now()
        return message + str(self.stop - self.start)

    def now(self, message="Now: "):
        """Returns the current time with a message"""
        return message + ": " + str(datetime.datetime.now())

    def elapsed(self):
        """Time elapsed since start was called"""
        return datetime.datetime.now() - self.start

    def split(self, message="Split started at: "):
        """Start a split timer"""
        self.split_start = datetime.datetime.now()
        return message + str(self.split_start)

    def unsplit(self, message="Unsplit: "):
        """Stops a split. Returns the time elapsed since split was called"""
        return message + str(datetime.datetime.now() - self.split_start)


#initialize variables
datref = 'C:/Users/bjb40/Dropbox/tracker_data/daily_tasks.csv'
current = date.today()
today = current.strftime('%m-%d')
hour = now.strftime("%H:%M")

con = dbapi.connect('C:/Users/bjb40/Dropbox/tracker_data/admin.db')
cur = con.cursor()
#moving from unicode to text : 
con.text_factory = str

#list high level tasks
def todo():
    print("\nCurrent high-level task list:\nPriority  | Deadline   | Countdown to  Task")
    cur.execute('SELECT priority, task, deadline, project FROM todo WHERE complete is null ')
    for i in cur.fetchall():
        deadline = datetime.datetime.strptime(i[2],"%Y,%m,%d")
        left = deadline.date() - current
        print(" %d        | %s      | %s days to %s" % (i[0], deadline.strftime('%m-%d'), left.days, i[1]))
    print ("\n\n")

plist = {}
cur.execute('SELECT project_name,production FROM projects')
for name, prod in cur.fetchall():
    plist[name] = prod 

#request input variables
loc = raw_input("Location(string): ")
todo()
task = raw_input("What is the task: ")
tag = raw_input("Project name: ")

#start timer
go = Timer()
go.start()

#Load Timer Messages
hours_day = 0.
hours_month = 0.
phours_month = 0.
hours_week = 0.

daysdat = pandas.read_csv('C:/Users/bjb40/Dropbox/tracker_data/plan-' + str(today)[0:2] + '-2015.csv')
days_month = 0
days_week = 0
for i in range(len(daysdat)):
    if daysdat["holiday"][i] == 0 and daysdat["weekday"][i] < 5:
        if datetime.datetime.strptime(daysdat["day"][i],"%m-%d").date().day < current.day:
            days_month += 1.


pdat = pandas.read_csv(datref)

for i in range(0,len(pdat)):
    if str(pdat['date'][i])[0:2] == str(today)[0:2]:
           hours_month += float(pdat['min_spent'][i])
           if pdat['project'][i] in plist:
               if str(pdat['date'][i]) != str(today):
                   if plist[pdat['project'][i]] == 'True':
                       phours_month += float(pdat['min_spent'][i])
           else:
               print('\n\n\tDATABASE ERROR: %s is not in database -- check for correctness.\n\n' % pdat['project'][i])

           if str(pdat['date'][i]) == str(today):
               hours_day += float(pdat['min_spent'][i])
               hours_month -= float(pdat['min_spent'][i])


print ('\nHours today so far:                             %.2f' % float(hours_day/60.))

if float(days_month) > 0:
    avhours_month = hours_month/(60.*float(days_month))
    avphours_month = phours_month/(60.*float(days_month))
    print ("Average hours per workday (" + str(days_month) + ") this month:     %.2f" % avhours_month )
    print ('\n\nCurrent conversion rate (target=1.25):          %.2f' % float(avhours_month/8.) )
    print (    'Current production ratio(target=0.60):          %.2f' % float(avphours_month/avhours_month) )
else:
    print ("\n\nFirst day of the month - good luck!")


#Request timer completion
complete = raw_input("Task timer begun at \n" + str(go.start) + "\n\n\nEnter 1 (complete) or 0 (incomplete) to stop: ")
go.stop()


#return minutes from timer
min_spent = go.elapsed().seconds//60.

#Add data to time tracker
newline = today,hour,loc,task,tag,min_spent,int(complete)

#apend new row:
with open(datref, 'a') as csvfile:
    csv.writer(csvfile, lineterminator="\n").writerow(newline)

success = "failed"

if int(complete) == 1:
    success = "succeeded"

print "Appending to data . . . \n\n\nMinutes Spent:", min_spent
print "Task " + success + ".\n\n\n\n"
hours_day += float(min_spent)
print ("Hours today now " + str(round(hours_day/60.,2)) + ".")

