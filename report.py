"""

This collects a number of reporting tasks and reviews database.
Requires a pre-defined databese with a number of tables. Note that all date objects are 
transformed into a string the Year,month,day e.g. '2014,10,25' is October 25, 2014

Projects Table
    number{k}: interger (also unique key)
    name: text
    description: text
    notes: text
    collaborators: text (names separated by semicolons)
    production: binary (true means that it is leading to publicaiton)
    phase: interger (1 to 4) 1=investigation; 2=analysis; 3=production; 4=post-production; 0=abandoned or 

Transitions Table
    number{k}: integer <-> Projects
    name: text <-> Projects
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
       'Plan a month:               makeplan(month,year) (month is two digits, year is four digits) \n' +
       'Create a monthly report:    makereport(month, year) (month is two digits, year is four digits\n' + 
'Start a new project:        newproject()\n' +
'Print Summary of Project:   projectsum()\n')

# import dependencies

import time, datetime
from datetime import date, timedelta as td
import sqlite3 as dbapi
import calendar

#universal stats

#This is the pin for planned working hours per work day.
planperday = 8.

# import data

datref = 'C:/Users/bjb40/Dropbox/tracker_data/daily_tasks.csv'
plandir = 'C:/Users/bjb40/Dropbox/tracker_data/'

con = dbapi.connect('C:/Users/bjb40/Dropbox/tracker_data/admin.db')
cur = con.cursor()
# moving from unicode to text : 
con.text_factory = str

# prepare a funciton to populate database for  monthly planning purposes
# need to create an overwrite check 
def makeplan(month,year):
    '''
    Input a month to create a print-out of the month.
    '''
    start_date = date(year, month, 1)
    end_date = date(year, month, calendar.monthrange(year,month)[1]) # need to fix year 

    delta = end_date - start_date

    for i in range(delta.days + 1):
        dt = (start_date + td(days=i)).strftime('%Y-%m-%d %H:%M:%S')
        wkday = int((start_date + td(days=i)).weekday())
        print('writing '+ str(dt) + str(wkday))
        cur.execute("INSERT INTO plan (datecol,weekday,holiday) VALUES (?, ?, ?)", (dt,wkday,0))
 
    con.commit()

# to be depricated once all of the database stuff is up:

    plan = open(plandir + str(month) + '-2015.csv', 'a')
    plan.write('day,weekday')

    for i in range(delta.days + 1):
        print('writing '+ (start_date + td(days=i)).strftime('%m-%d') )
        plan.write("\n'" + (start_date + td(days=i)).strftime('%m-%dd')[1:-1] + "'," )
        plan.write(str((start_date + td(days=i)).weekday()))

    print('now closing')
    plan.close()

#make a simple report based on previous plan
def makereport(month, year):
    '''
    Create a time report based on an input of month and year, for example, to make September 2014 report, 
    use makereport(09,2014).
    '''

    import scipy as sp
    import csv
    import pandas
    #>> Read in the data #
    repmonth = str(month)
    if len(repmonth) == 1:
        repmonth = '0' + repmonth

    repyear = str(year)
    repdate = datetime.datetime.now()
    pdat = pandas.read_csv(datref)
    #print(plandir + 'plan-' + repmonth + '-' + repyear + '.csv')
    daysdat = pandas.read_csv(plandir + 'plan-' + repmonth + '-' + repyear + '.csv')

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
    pworked = 0.
    project_mins = {}
    #identify "production projects" from database
    plist = {}
    cur.execute('SELECT project_name,production FROM projects')
    for name, prod in cur.fetchall():
        plist[name] = prod 

    for i in range(0,len(pdat)):
        #print pdat['date'][i]
        if str(pdat['date'][i])[0:2] == repmonth:
            worked += float(pdat['min_spent'][i])
            if pdat['project'][i] in plist:
                if plist[pdat['project'][i]] == 'True':
                    pworked += float(pdat['min_spent'][i])
            else:
                print(pdat['project'][i] + ' recorded on ' + pdat['date'] + ' is not in database -- check for correctness.')

            if pdat['project'][i] in project_mins:
                project_mins[pdat['project'][i]] += float(pdat['min_spent'][i])
                #print('old' + str(pdat['project'][i]))
        
            else:
                project_mins[pdat['project'][i]] = float(pdat['min_spent'][i])

    #output stats
    hours = worked/60.
    prodhours = pworked/60.
    avperday = worked/(float(workdays)*60.)
    avproday = pworked/(float(workdays)*60.)
    convrate = avperday/planperday
    prodratio = avproday/avperday

    #>> call pandoc and build a .pdf or .html or .docx document for printing#
    reported = plandir + repyear + '-' + repmonth + '-report.md'
    makerep = open(reported, 'w')

    #yaml header
    makerep.write('---\nauthor: Bryce Bartlett\ndate: {0:%B} {0:%d}, {0:%Y} \ntitle: {1} Report\n---\n\n'.format(repdate,calendar.month_name[int(month)]))

    #output for monthly overview
    makerep.write('#Overview#\n\n')
    makerep.write('Planned for ' + str(workdays) + ' days of work in August.\n\n')
    makerep.write('Worked a total of %.2f hours, ' % hours)
    makerep.write('which amounts to an average of %.2f hours per work day.\n\n' % avperday)
    makerep.write('Of this, %.2f hours, or %.2f per day, was work directly related to publication.\n\n\n' % (prodhours, avproday))
    makerep.write('#Production Statistics:#\n\n')

    #key monthly statistics
    makerep.write('**Conversion Rate:       %.3f** \n\n' % convrate )
    makerep.write('**Production Ratio:      %.3f** \n\n' % prodratio )
    makerep.write('**Transition Time:       tbd** \n\n\n')

    #output for overview of projects
    makerep.write('#Projects#\n\n')

    for i in project_mins:
        #print i
        makerep.write('\n\n##' + str(i) + ': ' + str(round(project_mins[i]/60.,2)) + ' hours#\n\n\n\n')
        makerep.write('|Date | Task | Hours |\n')
        makerep.write('|----------|-------------------------------------|-------|\n')
    
        for j in range(0,len(pdat)):
            if pdat['project'][j] == i and str(pdat['date'][j])[0:2] == repmonth:
                #print(pdat['project'][j],i)
                makerep.write('| ' + str(pdat['date'][j][3:5]) + ' | ' + str(pdat['task'][j]) + ' | ' + str(round(pdat['min_spent'][j]/60.,2)) + '|\n')

    makerep.close()

    # call pandoc to make it a docx -- doesn't format correctly
#    import os,subprocess

#    fileout = os.path.splitext(reported)[0] + '.docx'
#    args1 =  ['cd',os.path.split(reported)[0]]
#    print(args1)
#    args2 =  ['pandoc', '-s','-S', os.path.split(reported)[1], '-o', os.path.split(fileout)[1]]
#    print(args2)
#    subprocess.Popen(args1)
#    subprocess.Popen(args2)
#    print subprocess.check_call(args1)

def newproject():
    ''' 
    Input new project into exesiting sqlite3 database.
    All dates are strings of the form '%Y,%m,%d', or 2014,10,24 for October 24, 2014.
    '''
#cur.execute('CREATE TABLE projects(number INTERGER, project_name TEXT, description TEXT, notes TEXT, collab TEXT, production BINARY, phase INTERGER, start_date TEXT, analysis_date TEXT, production_date TEXT, postproduction_date TEXT, published_date TEXT, abandoned_date TEXT, citation TEXT)') 

    import datetime
    start_date = datetime.datetime.now().strftime('%Y,%m,%d')
#    print start_date.strftime('%Y,%m,%d')
    name = raw_input("Name: ")
    description = raw_input("Description: ")
    collab = raw_input("Collaborators: ")
    production = raw_input("Production project (binary, True or False): ")
    notes = raw_input("Any notes: ")

    #assign index number as 1 plus prior largest
    cur.execute('SELECT MAX(number) FROM projects')
    newnum = cur.fetchall()[0][0] + 1

    print 'Creating record with the following values:'
    print (1,name,description,notes,production,1,start_date,'','','','','','','')

    cur.execute('INSERT INTO projects VALUES(?,?,?,?,?,?,?,?,NULL,NULL,NULL,NULL,NULL,NULL)', (newnum,name,description,notes,collab,production,1,start_date))

    con.commit()
    

# looking up name and structure cur.execute('pragma table_info(<tablename>)')
# looking up in table cur.execute(SELECT <column1>, <column2> FROM <table>') * gets all
# moving from unicode to text : con.text_factory = str

def projectsum():
    '''
    Prints list of projects and summarizes times and dates.
    '''
    
    cur.execute('SELECT project_name FROM projects')
    p_list = cur.fetchall()
    for i in p_list:
        print i[0]
    
    p = raw_input("Identify wich project (listed above) you want summarized: ")
    import scipy as sp
    import csv
    import pandas
    # Read the data
    pdat = pandas.read_csv(datref)
    worked = 0. # counter for minutes

    #Iterate through entire list
    for i in range(0,len(pdat)):
        if pdat['project'][i] == p:
            worked += float(pdat['min_spent'][i])

    hours = round(worked/60.,3)
    print 'Worked on ' + p + ' %.3f hours.' % hours 

    #For analyzing transition time -- later
#    import datetime
#    today = datetime.datetime.now()


