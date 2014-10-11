"""

This collects a number of reporting tasks and reviews database.
Requires a pre-defined databese with a number of tables.
Projects Table
    number: interger (also unique key)
    name: text
    description: text
    notes: text
    collaborators: text (names separated by semicolons)
    production: binary (true means that it is leading to publicaiton)
    phase: interger (1 to 4) 1=investigation; 2=analysis; 3=production; 4=post-production
    start_date: date (date investigation begun)
    analysis_date: date (date analysis begun)
    production_date: date(date writing--for publication--begun)
    postproduction_date: date (date submitted for publication)
    published_date: date (date published)
    abandoned_date: date shelved b/c it is not going to work
    citation: text
note - all dates are python date objects converted to intergers

Time Table

Plan Table

Notes Table

"""

print ('Functions:\n\n' +
'Plan a month:            makeplan(month)\n' +
'Create a monthly report: makereport(month)\n' + 
'Start a new project:     newproject\n')

# import dependencies

from datetime import date, timedelta as td
import sqlite3 as dbapi

# import data

datref = 'C:/Users/Bryce/Dropbox/tracker_data/daily_tasks.csv'
plandir = 'C:/Users/Bryce/Dropbox/tracker_data/'

db = dbapi.connect('C:/Users/Bryce/Dropbox/tracker_data/admin.db')
cur = db.cursor()

# prepare a funciton to populate a .csv for monthly planning purposes 
def makeplan(month):
    '''
    Input a month to create a print-out of the month.
    '''
    start_date = date(2014, month, 1)
    end_date = date(2014, month, 31) #need to write break because not all months have 31 days

    delta = end_date - start_date

    plan = open(plandir + str(month) + '-2014.csv', 'a')

    plan.write('day,weekday')

    for i in range(delta.days + 1):
        print('writing '+ (start_date + td(days=i)).strftime('%m-%d') )
        plan.write("\n'" + (start_date + td(days=i)).strftime('%m-%dd')[1:-1] + "'," )
        plan.write(str((start_date + td(days=i)).weekday()))
        
    print('now closing')
    plan.close()


#make a simple report based on previous plan
def makereport(month):
    '''
    Create a time report based on an input of the month -- two digit number which must be input
    as string (i.e. to make Septermber report, use makereport('09').
    '''

    import scipy as sp
    import csv
    import pandas
    #>> Read in the data #
    repmonth = str(month)
    pdat = pandas.read_csv(datref)
    daysdat = pandas.read_csv(plandir + 'plan-' + repmonth + '-2014.csv')

    # set counter for workdays
    workdays = 0

    #count weekdays for workdays
    for i in daysdat['weekday']:
        if i < 5.: 
            workdays +=1 

    #subtract holiday and vacation days from workdays
    for i in daysdat['holiday']:
        workdays -= i

    #>> Prepare simple .md output for outputing to pandoc #
    worked = 0.
    project_mins = {}

    for i in range(0,len(pdat)):
    #   print pdat['date'][i]
        if str(pdat['date'][i])[0:2] == repmonth:
            worked += float(pdat['min_spent'][i])

            if pdat['project'][i] in project_mins:
                project_mins[pdat['project'][i]] += float(pdat['min_spent'][i])
                #print('old' + str(pdat['project'][i]))
        
            else:
                project_mins[pdat['project'][i]] = float(pdat['min_spent'][i])



    #>> call pandoc and build a .pdf or .html or .docx document for printing#
    reported = plandir + repmonth + '-report.md'
    makerep = open(reported, 'w')

    #yaml header
    makerep.write('---\nauthor: Bryce Bartlett\ndate: September 2014 \ntitle: August Report\n---\n\n')

    #output for monthly overview
    makerep.write('#Overview\n\n')
    makerep.write('Planned for ' + str(workdays) + ' days of work in August.\n\n')
    makerep.write('Worked a total of ' + str(round(worked/60.,3)) + ' hours, ')
    makerep.write('which amounts to an average of ' + str(round(worked/(float(workdays)*60.),2)) + ' hours per work day.\n\n\n')

    #output for overview of projects
    makerep.write('#Projects\n\n')

    for i in project_mins:
        makerep.write('\n\n##' + str(i) + ': ' + str(round(project_mins[i]/60.,2)) + ' hours\n\n\n\n')
        makerep.write('|Date | Task | Hours |\n')
        makerep.write('|----------|-------------------------------------|-------|\n')
    
    for j in range(0,len(pdat)):
        if pdat['project'][j] == i and str(pdat['date'][j])[0:2] == repmonth:
            makerep.write('| ' + str(pdat['date'][j][3:5]) + ' | ' + str(pdat['task'][j]) + ' | ' + str(round(pdat['min_spent'][j]/60.,2)) + '|\n')

    makerep.close()

    # call pandoc to make it a docx
    import os,subprocess

    fileout = os.path.splitext(reported)[0] + '.docx'
    args =  ['pandoc', reported, '-o', fileout, '-s']
    print(args)
    subprocess.Popen(args, stdout=subprocess.PIPE)
    print subprocess.call(args)

def newproject():
    '''
    Input new project into exesiting sqlite3 database.
    '''
#cur.execute('CREATE TABLE projects(number INTERGER, description TEXT, notes TEXT, collab TEXT, production BINARY, phase INTERGER, start_date REAL, analysis_date REAL, production_date REAL, postproduction_date REAL, published_date REAL, abandoned_date REAL, citation REAL)') 

    import datetime
    start_date = datetime.datetime.now()
    print start_date
 
#    rawinput

    


 
