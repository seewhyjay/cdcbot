import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import os
import requests
import time
from selenium.webdriver.common.keys import Keys
import pickle
from conn import getconn
import pymysql

KEY = os.environ.get("azcaptcha_key")
LEARNER_ID = os.environ.get("LEARNER_ID")
PASSWORD = os.environ.get("PASSWORD")


def convertToBinaryData(filename):
    #Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
    CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
    driver.get("https://www.cdc.com.sg/")
    login_button = driver.find_element_by_xpath("/html/body/div[3]/div/ul/li[10]/a").click()
    captcha_iframe = driver.find_element_by_xpath("/html/body/div[8]/div/form/div[3]/div")
    outer_html = captcha_iframe.get_attribute("outerHTML")
    src = outer_html.split(' ')[2]
    sitekey = src.split('"')[1]
    response_box = driver.find_element_by_xpath('//*[@id="g-recaptcha-response"]')
    # response_box is a hidden element, change display = none to display=block to make it accessible by keyboard
    driver.execute_script('document.getElementById("g-recaptcha-response").style.display = "block";')
    parse_url_in = f"http://azcaptcha.com/in.php?key={KEY}&method=userrecaptcha&googlekey={sitekey}&pageurl=https://www.cdc.com.sg/#"
    # Get ID from azcaptcha
    reqin = requests.get(parse_url_in)
    id = (reqin.text).split("|")[1]
    parse_url_out = f"http://azcaptcha.com/res.php?key={KEY}&action=get&id={id}"
    reqout = requests.get(parse_url_out)
    # Wait for captcha to be completed
    while (reqout.text).split("|")[0] != "OK":
        print(reqout.text)
        reqout = requests.get(parse_url_out)
        time.sleep(5)
    captcha_response = (reqout.text).split("|")[1]
    response_box.send_keys(captcha_response)
    username = driver.find_element_by_xpath("/html/body/div[8]/div/form/div[1]/input").send_keys(LEARNER_ID)
    enter_password = driver.find_element_by_xpath("/html/body/div[8]/div/form/div[2]/input").send_keys(PASSWORD)
    login = driver.find_element_by_xpath("/html/body/div[8]/div/form/div[4]/input").click()
    pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
    conn = getconn()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM auth WHERE id=1")
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO auth (id, cookie) VALUES (1, %s)", pymysql.Binary(convertToBinaryData("cookies.pkl"))) 
    conn.commit()
    driver.close()

if __name__ == '__main__':
    main()