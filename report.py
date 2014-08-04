"""

This puts simple monthly report together.

"""

# import dependencies

from datetime import date, timedelta as td

# import data

datref = 'J:/Bryce/python/time_tracker/data/daily_tasks.csv'

# prepare report as .md file (for export by pandoc)

start_date = date(2014, 7, 1)
end_date = date(2014, 7, 31)

delta = end_date - start_date

for i in range(delta.days + 1):
    print (start_date + td(days=i)).strftime('%m-%d')
    print (start_date + td(days=i)).weekday()

