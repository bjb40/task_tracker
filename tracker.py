#!python3.5
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
import re

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
ty = current.strftime('%Y')
hour = now.strftime("%H:%M")

con = dbapi.connect('C:/Users/bjb40/Dropbox/tracker_data/admin.db')
cur = con.cursor()
#moving from unicode to text : 
con.text_factory = str

#lists high level tasks--don't use/consider deleting
def todo():
    print("\nCurrent high-level task list:\nPr |Project\t|Deadline | Countdown to  Task\n")
    cur.execute('SELECT priority, task, deadline, project FROM todo WHERE complete is null ')
    order = sorted([(i[0],datetime.datetime.strptime(i[2],"%Y,%m,%d"),i[1],i[3]) for i in cur.fetchall()])

    for i in order:
        deadline = i[1]
        left = deadline.date() - current
        print(" %d |%s\t| %s   | %s days to %s" % (i[0], i[3][0:10],deadline.strftime('%m-%d'), left.days, i[2]))
    print ("\n\n")

#id key tasks (can make dynamic based on topic models): (1) code, (2) write, (3) revise
tasktype={
    'writing' : re.compile('wr[io]t[eing]+',re.IGNORECASE),
    'coding' : re.compile('cod[eing]+',re.IGNORECASE),
    'revising' : re.compile('revis[ionged]',re.IGNORECASE)
}

pdat = pandas.read_csv(datref)

##should use this to simplify code above; instead of looping
pdatm=pdat[pdat['date'].str.contains(str(current.month)+'-')]
print('---------------------\nKey Task Overview:\n---------------------\n')

if sum(pdatm['min_spent']) == 0:
    print('Beginning of Month: Here are last month\'s figures\n')
    pdatm=pdat[pdat['date'].str.contains(str(current.month-1)+'-')]

for t in tasktype.keys():
    prop=sum(pdatm[pdatm['task'].str.contains(tasktype[t])]['min_spent'])/sum(pdatm['min_spent'])
    print('Proportion of month spent %s:\t %.2f' % (t,prop))

print('\n\nNote: not mutually exclusive...\n---------------------\n')

    
plist = {}
cur.execute('SELECT project_name,production FROM projects')
for name, prod in cur.fetchall():
    plist[name] = prod 

#request input variables
loc = input("Location(string): ")
#todo()
task = input("What is the task: ")
tag = input("Project name: ")

#start timer
go = Timer()
go.start()

#Load Timer Messages
#hours actually track minutes - variables need renamed
hours_day = 0.
hours_month = 0.
phours_month = 0.
hours_week = 0.

daysdat = pandas.read_csv('C:/Users/bjb40/Dropbox/tracker_data/plan-' + str(today)[0:2] + '-' + ty + '.csv')
tot_month = 0
days_month = 0
days_week = 0
conv_target = 1.25
prod_target = 0.6

for i in range(len(daysdat)):
    if daysdat["holiday"][i] == 0 and daysdat["weekday"][i] < 5:
        #pull day and month from plan, and add current year
        d = daysdat["day"][i] + '-'+ str(current.year)
        #transform to datetime object
        dt = datetime.datetime.strptime(d,"%m-%d-%Y")
        tot_month += 1.
        if dt.date().day < current.day:
            days_month += 1.

min_need = tot_month*8.*conv_target*60.
prod_need = min_need*prod_target

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

days_left = float(tot_month - days_month)

#you can probably simplify this...
if days_left>0:
    avhours_need = (min_need - hours_month) / (60.*days_left)
    avprod_need = (prod_need - phours_month) / (60.*days_left)
else:
    avhours_need = (min_need - hours_month) / 60.
    avprod_need = (prod_need -phours_month) /60.

    
print ('\n%.0f days worked this month; %.0f remaining.' % (float(days_month), float(days_left)) )
print ('Hours today so far:                       %.2f\n\n' % float(hours_day/60.))

if float(days_month) > 0:
    avhours_month = hours_month/(60.*float(days_month))
    avphours_month = phours_month/(60.*float(days_month))
  

    print ('Total hours worked so far this month:     %.2f' % float(hours_month/60.) )
    print ('Average hours per workday this month:     %.2f' % avhours_month )
    print ('Average hours needed now:                 %.2f' % float(avhours_need) )
    print ('Production hours per day needed:          %.2f\n' % float(avprod_need)  ) 
    print ('\nCurrent conversion rate (target=%.2f):    %.2f' % (float(conv_target),float(avhours_month/8.)) )
    print (  'Current production ratio(target=%.2f):    %.2f' % (float(prod_target),float(avphours_month/avhours_month)) )


else:
    print ("\n\nFirst day of the month - good luck!")


#Request timer completion
complete = input("\nTask timer begun at \n" + str(go.start) + "\n\n\nEnter 1 (complete) or 0 (incomplete) to stop: ")
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

print ("Appending to data . . . \n\n\nMinutes Spent:", min_spent)
print ("Task " + success + ".\n\n\n\n")
hours_day += float(min_spent)
print ("Hours today now " + str(round(hours_day/60.,2)) + ".")



