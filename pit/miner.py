import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import re


def update_sqlite():
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


def calculate_ema(price_list, period):
    ema_list = []
    for price in price_list:
        try:
            ema = ((price * 2) / (period+1)) + ((ema_list[-1] * (period-1)) / (period+1))
            ema_list.append(ema)
        except IndexError:
            ema_list.append(price)
    return ema_list


def calculate_dif(ema_list0, ema_list1):
    dif_list = [ema0 - ema1 for ema0, ema1 in zip(ema_list0, ema_list1)]
    return dif_list


def get_first_date_index_in_month(date_list):
    first_date_index_list, month_now = [], date_list[0].month
    for date in date_list:
        if date.month != month_now:
            first_date_index_list.append(date_list.index(date))
            month_now = date.month
    return first_date_index_list


def separate_macd_list(macd_list):
    positive_macd_list, negative_macd_list = [], []
    for macd in macd_list:
        if macd > 0:
            positive_macd_list.append(macd)
            negative_macd_list.append(0)
        elif macd < 0:
            positive_macd_list.append(0)
            negative_macd_list.append(macd)
        else:
            positive_macd_list.append(0)
            negative_macd_list.append(0)

    return positive_macd_list, negative_macd_list


def datetime_to_str(date_list):
    str_list = [date.strftime('%Y/%m/%d') for date in date_list]
    return str_list
