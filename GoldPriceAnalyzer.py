import sqlite3
from matplotlib import pyplot
from datetime import datetime


conn = sqlite3.connect('goldprice.sqlite')
cur = conn.cursor()

cur.execute('SELECT * FROM Gold ORDER BY Date ASC')
all_fetch = cur.fetchall()

date_list, price_in_list, price_out_list = ([], [], [])

for date, price_out, price_in in all_fetch:
    date_list.append(date)
    price_out_list.append(price_out)
    price_in_list.append(price_in)

converted_dates = map(datetime.strptime, date_list, len(date_list)*['%Y/%m/%d'])
x = list(converted_dates)

pyplot.subplot(211)
pyplot.ylabel('Price sold out')
pyplot.plot(x, price_out_list)

pyplot.subplot(212)
pyplot.xlabel('Date')
pyplot.ylabel('Price buy in')
pyplot.plot(x, price_in_list)

pyplot.show()
