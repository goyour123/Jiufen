import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import re


conn = sqlite3.connect('goldprice.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Gold (Date TEXT UNIQUE, Price_Out INTEGER, Price_In INTEGER)''')

cur.execute('''SELECT Date FROM Gold''')
db_date = [db_date for db_date, in cur.fetchall()]

url = "http://rate.bot.com.tw/gold/chart/year/TWD"

res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')
table = soup.find('table', {'class': 'table table-striped table-bordered table-condensed table-hover toggle-circle'})
tbody = table.tbody.findAll('tr')

for tr in tbody:
    date = tr.find('a').string
    if date in db_date:
        break
    price = tr.findAll('td', {'class': 'text-right'})
    cur.execute('''INSERT OR IGNORE INTO Gold (Date, Price_In, Price_Out) VALUES (?, ?, ?)''',
                (date,
                 int(price[0].string),
                 int(price[1].string)))

conn.commit()
