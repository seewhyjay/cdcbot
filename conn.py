import peewee
from peewee import *
import pymysql

def getconn():
    conn = MySQLDatabase('', user='', password='',
                        host='', port=3306)
    return conn