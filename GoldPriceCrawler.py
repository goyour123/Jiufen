import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import re

conn = sqlite3.connect('goldprice.sqlite')
cur = conn.cursor()

# cur.execute('''
# DROP TABLE IF EXISTS Gold''')
#
# cur.execute('''
# CREATE TABLE Gold (Date TEXT UNIQUE, Price_Out INTEGER, Price_In INTEGER)''')

url = "http://rate.bot.com.tw/Pages/UIP005/UIP005INQ3.aspx?view=1&lang=zh-TW"

payload = {
    '__VIEWSTATE': '/wEPDwULLTE3ODAwNTkwNTFkGAIFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYHBQZSYWRpbzUFBlJhZGlvMQUGUmFkaW8yBQZSYWRpbzMFBlJhZGlvNAUFY3RsMDIFBWN0bDAzBQltdWx0aVRhYnMPD2QCAWQIrRIWn14+pxO1s0LxNTzpJDewpg==',
    '__VIEWSTATEGENERATOR': '5D1BFF76',
    '__EVENTVALIDATION': '/wEdAA5Ga+nSqjK5uUye/4lqnHhxp7+cQefjgloeOmoWSbn28rmIL5vrvRo+chN0IrYmv1mTkKDhwt9/WQNeB4ViuWNgcMx0/4kN+q4HQkIfmt6OsgcYUqaeErR2FzC2w/TY+YGZQ64G7aavBrw885NMMoQrQLiSjRHUjGqETsET1vMRZ5SFaW19BRC0Lg5Jpx0kgWSC71UtEOrfb/oUZNhY9MQCXFWqB4QKYjYFCvvDmQ0Nk8kCKvP8wJMd+eRMYfuMWi/N+DvxnwFeFeJ9MIBWR6935bDqD1t67/Yn/Stpk4YjYQlQPvoZofb9D+nPE9N62lcHYeg7',
    'term': '3',
    'year': str(datetime.now().year),
    'month': str(datetime.now().month),
    'curcd': 'TWD',
    'afterOrNot': '0',
    'Button1': '查詢'
}
res = requests.post(url, data=payload)

soup = BeautifulSoup(res.text, 'html.parser')

row = (soup.findAll('tr', {'class': re.compile('color[01]')}))

date, price = ([], [])

for item0 in row:
    price = item0.findAll('td', {'class': 'decimal'})
    cur.execute('''INSERT OR IGNORE INTO Gold (Date, Price_Out, Price_In) VALUES (?, ?, ?)''',
                (item0.a.string,
                 int(price[0].string),
                 int(price[1].string)))

conn.commit()
