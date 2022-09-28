import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession
import inspect
from bs4 import BeautifulSoup
from datetime import datetime
import time
import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(host='sneakifox.myasustor.com',
                                         database='root',
                                         user='Melina1025',
                                         password='Sneaker')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")