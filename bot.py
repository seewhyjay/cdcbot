from flask import Flask, request
import telegram
import time
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import os
from skimage.metrics import structural_similarity as compare_ssim
import imutils
import cv2
import pymysql
from conn import getconn
import pickle

global bot
global TOKEN
URL = ''
TOKEN = ''
user_id = ''

bot = telegram.Bot(token=TOKEN)


app = Flask(__name__)

# Feel free to reimplement all the comparing stuff so the bot doesn't spam you

def compare(image1, image2):
    imageA = cv2.imread(image1)
    imageB = cv2.imread(image2)
    # convert the images to grayscale
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # compute the Structural Similarity Index (SSIM) between the two
    # images, ensuring that the difference image is returned
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype("uint8")
    print("SSIM: {}".format(score))
    return score

def changes(image1, image2):
    imageA = cv2.imread(image1)
    imageB = cv2.imread(image2)
    # convert the images to grayscale
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # compute the Structural Similarity Index (SSIM) between the two
    # images, ensuring that the difference image is returned
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype("uint8")
    print("SSIM: {}".format(score))
    thresh = cv2.threshold(diff, 0, 255,
        cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # Image Difference with OpenCV and Python
    # loop over the contours
    for c in cnts:
        # compute the bounding box of the contour and then draw the
        # bounding box on both input images to represent where the two
        # images differ
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(imageA, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.rectangle(imageB, (x, y), (x + w, y + h), (0, 0, 255), 2)
    cv2.imwrite(f"{image1}_changes.png", imageA)
    return f"{image1}_changes.png"


def writeTofile(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored blob data into: ", filename, "\n")
 
def convertToBinaryData(filename):
    #Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

def update_cookies():
    conn = getconn()
    with conn.cursor() as cur:
        cur.execute("SELECT cookie FROM auth")
        cookie = cur.fetchone()[0]
        writeTofile(cookie, "cookies.pkl")
    return "Updated cookies"


def screenshotAndSend():
    conn = getconn()
    # Download cookies if it doesn't exist yet
    if not os.path.exists("cookies.pkl"):
        update_cookies()

    # All of these are to get selenium to work on Heroku
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
    # Set window size to get better screenshots, might have to update, CDC updated their website within the last few months
    driver.set_window_size(1920, 1080)
    # To load cookies, you need to be on the same domain
    driver.get('https://www.cdc.com.sg/')
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
            driver.add_cookie(cookie)
    driver.get("https://www.cdc.com.sg:8080/NewPortal/Booking/Dashboard.aspx?")
    time.sleep(2)
    # Check if cookies have expired
    if driver.current_url != "https://www.cdc.com.sg:8080/NewPortal/Booking/Dashboard.aspx?":
            bot.send_message(user_id, text="Cookies expired, please upload new ones")
            return "Failed"
    print('Logged in')
    practical_lessons = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr/td[1]/table/tbody/tr/td/div/table/tbody/tr[2]/td[2]/table/tbody/tr[2]/td/div/div/div[1]/table[5]/tbody/tr/td[4]/a').click()
    time.sleep(2)
    # Will always select 2nd option which in this case is class3a, so it's fine
    class3 = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/div/table/tbody/tr[3]/td/table/tbody/tr[1]/td/table/tbody/tr[1]/td[1]/div/table/tbody/tr[1]/td[2]/select/option[2]').click()
    time.sleep(2)
    print('Screenshotting tables')
    table = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/div/table/tbody/tr[3]/td')
    table.screenshot("page1.png")
    time.sleep(2)
    # This whole block is in a try except block because there are usually no more lessons, so the 'next arrow' element might not exist
    try:
        page_2 = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[1]/td/div/table/tbody/tr/td/input[2]').click()
        table2 = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/div/table/tbody/tr[3]/td')
        time.sleep(2)
        table2.screenshot("page2.png")
        page_3 = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[1]/td/div/table/tbody/tr/td/input[2]').click()
        time.sleep(2)
        table3 = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/div/table/tbody/tr[3]/td')
        table3.screenshot("page3.png")
        page_4 = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[1]/td/div/table/tbody/tr/td/input[2]').click()
        time.sleep(2)
        table4 = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/div/table/tbody/tr[3]/td')
        table4.screenshot("page4.png")
    except:
        # Deletes the older pictures so it doesn't send outdated images
        pictures = ['page2.png', 'page3.png', 'page4.png']
        for picture in pictures:
            if os.path.exists(picture):
                os.remove(picture)
    simulator = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr/td[1]/table/tbody/tr/td/div/table/tbody/tr[2]/td[2]/table/tbody/tr[2]/td/div/div/div[1]/table[6]/tbody/tr/td[4]/a').click()
    time.sleep(2)
    sim_lessons = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/div/table/tbody/tr[3]/td/table/tbody/tr[1]/td/div/table/tbody/tr[1]/td[2]/select/option[2]').click()
    time.sleep(2)
    sim_table = driver.find_element_by_xpath('/html/body/form/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/div/table/tbody/tr[3]/td')
    sim_table.screenshot("sim.png")
    
    driver.close()
    bot.send_message(user_id, text='Class 3 Lessons')
    bot.send_photo(user_id, photo=open('page1.png', 'rb'))
    try:
        bot.send_photo(user_id, photo=open('page2.png', 'rb'))
        bot.send_photo(user_id, photo=open('page3.png', 'rb'))
        bot.send_photo(user_id, photo=open('page4.png', 'rb'))
    except:
        pass
    bot.send_message(user_id, text='Simulator Lessons')
    bot.send_photo(user_id, photo=open('sim.png', 'rb'))


# Request this url every minute to keep cookie alive
@app.route("/keepalive")
def keepalive():
    if not os.path.exists("cookies.pkl"):
        print("Updating cookies")
        update_cookies()
    GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
    CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
    driver.set_window_size(1920, 1080)
    driver.get('https://www.cdc.com.sg/')
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.get("https://www.cdc.com.sg:8080/NewPortal/Booking/Dashboard.aspx?")
    time.sleep(2)
    if driver.current_url != "https://www.cdc.com.sg:8080/NewPortal/Booking/Dashboard.aspx?":
        bot.send_message(user_id, text="You have been logged out, please upload a new cookie")
        driver.close()
        return "Cookie dead"
    driver.close()
    return "Still alive!"

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    print("got text message:", text, "from: ", chat_id)

    if text == 'changes' or text =='Changes':
        screenshotAndSend()
    elif text == "update":
        update_cookies()
    
    return 'ok'

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/ping')
def index():
    screenshotAndSend()
    return 'Pinged'


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', '8443'))
    app.run(threaded=True, port=PORT, host='0.0.0.0')