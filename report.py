"""

This puts simple monthly report together.

"""

# import dependencies

from datetime import date, timedelta as td

# import data

datref = 'C:/Users/bjb40/Dropbox/tracker_data/daily_tasks.csv'
plandir = 'C:/Users/bjb40/Dropbox/tracker_data/'

# prepare a funciton to populate a .csv for monthly planning purposes 
def makeplan(month):
    '''
    Input a month to create a print-out of the month.
    '''
    start_date = date(2014, month, 1)
    end_date = date(2014, month, 31)

    delta = end_date - start_date

    plan = open(plandir + str(month) + '-2014.csv', 'a')

    plan.write('day, weekday')

    for i in range(delta.days + 1):
        print('writing '+ (start_date + td(days=i)).strftime('%m-%d') )
        plan.write("\n'" + (start_date + td(days=i)).strftime('%m-%dd')[1:-1] + "'," )
        plan.write(str((start_date + td(days=i)).weekday()))
        
    print('now closing')
    plan.close()


#make a simple report based on previous plan

import scipy as sp
import csv
import pandas

#>> Read in the data #

pdat = pandas.read_csv(datref)
daysdat = pandas.read_csv(plandir + 'plan-7-2014.csv')

# set counter for workdays
workdays = 0

#count weekdays for workdays
for i in daysdat[' weekday']:
    if i < 5.: 
         workdays +=1 

#subtract holiday and vacation days from workdays
for i in daysdat['holiday']:
    workdays -= i


#>> Prepare simple .md output for outputing to pandoc #

worked = 0.

for i in range(0,len(pdat)):
    if str(pdat['date'][i])[1:3] == '07':
  #      print pdat[' min_spent'] 
        worked += float(pdat[' min_spent'][i])


#>> call pandoc and build a .pdf or .html or .docx document for printing#

reported = plandir + '07-report.md'

makerep = open(reported, 'w')

#yaml header
makerep.write('---\nAuthor:Bryce Bartlett\nDate:\nTitle:July Report\n---\n\n')

#output for monthly overview
makerep.write('Planned for ' + str(workdays) + ' days of work in July.\n\n')
makerep.write('Worked a total of ' + str(round(worked/60.,3)) + ' hours, ')
makerep.write('which amounts to an average of ' + str(round(worked/(float(workdays)*60.),2)) + ' hours per work day.\n\n\n')


#output for overview of projects



makerep.write('And something about the projects')


makerep.close()
