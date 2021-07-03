from conn import getconn
import pymysql
import pickle
import selenium.webdriver
import time


def convertToBinaryData(filename):
    #Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


driver = selenium.webdriver.Firefox(executable_path=r"C:\Users\admin\Downloads\Compressed\geckodriver.exe")
driver.get("https://www.cdc.com.sg/")
time.sleep(60)
pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))


conn = getconn()
a = convertToBinaryData("cookies.pkl")
print(a)
with conn.cursor() as cur:
    cur.execute("DELETE FROM auth WHERE id=1")
conn.commit()
with conn.cursor() as cur:
    cur.execute("INSERT INTO auth (id, cookie) VALUES (1, %s)", pymysql.Binary(convertToBinaryData("cookies.pkl"))) #, ('1', pymysql.Binary(a)))
conn.commit()
with conn.cursor() as cur:
    cur.execute("SELECT * FROM auth")
    b = cur.fetchone()
    print(b)