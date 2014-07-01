"""

 This is a multi-span comment with front matter

NOTE - I can prune a lot of these time variables up front because of the timer

"""


# import dependencies

#import time
#from datetime import date


from datetime import date, timedelta as td

# start and end dates

datref = 'J:/Bryce/python/time_tracker/data/daily_tasks.csv'

current = date.today()
today = current.strftime('%m-%d') 

start_date = date(2014, 6, 1)
end_date = date(2014, 6, 30)

#pull time

import time as now

hour = now.strftime("%H:%M")

#ask for task number

taskn = raw_input("Task number: ")

#ask for task text

task = raw_input("What is the task: ")

tag = raw_input("Project name: ")

#set end timer

import datetime

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

go = Timer()
go.start()

complete = raw_input("Task timer begun at \n" + str(go.start) + "\n\n\nEnter 1 (complete) or 0 (incomplete) to stop: ")
go.stop()

#return minutes from timer
min_spent = go.elapsed().seconds//60

newline = today, hour, int(taskn), task, tag, min_spent, int(complete)

#apend new row:
fd = open(datref,'a')
fd.write('\n'+str(newline)[1:-1])
fd.close()

success = "failed"

if int(complete) == 1:
    success = "succeeded"


print "Appending to data . . . \n\n\nMinutes Spent:", min_spent

print "Task " + success + "\n\n\n\n"



""" 
---->
Code below lists dates - use for report at later date
<----


delta = end_date - start_date

for i in range(delta.days + 1):
    print start_date + td(days=i)

"""
