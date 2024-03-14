from flask import Flask, request, render_template
import werkzeug
import json
from selenium import webdriver
from selenium.webdriver.common.by import By

import random
import time
from multiprocessing import Process, Manager
from pytz import timezone
from datetime import datetime

app = Flask(__name__)

OR_USERNAME = "sergey@ownerrez.com"
OR_PASS = "qqqQQQ111###"



def getCurrentTime():
    return datetime.now(timezone('EST')).strftime('%H:%M:%S')


def loop(on_off, python_log):
    def debug(text, python_log):
        print(text)
        python_log.append(text)
        if len(python_log) > 100:
            python_log = python_log[-100:-1]

    # Long pause every 45-70 minutes
    next_time_long_sleep = (time.time()) + (random.randint(45, 70) * 60)
    counters = {"all": 1, "edge": 1, "ff": 1, "chrome": 1}

    environment_urls = {"https://securetest-a.ownerrez.com",
                        "https://securetest-b.ownerrez.com",
                        "https://securetest-c.ownerrez.com",
                        "https://securetest-d.ownerrez.com",
                        "https://securetest-e.ownerrez.com",
                        "https://securestage.ownerrez.com"}
    # Reading all urls
    all_urls = readUrlsFromFile("orez_urls.txt")

    # Initializing webdrivers
    driverChrome = getDriver("chrome")
    driverFF = getDriver("ff")
    driverEdge = getDriver("edge")

    # Login to orez for all environments for each browser
    for driver in {driverFF, driverChrome, driverEdge}:
        for url in environment_urls:
            loginToOR(driver=driver, environmentUrl=url)

    debug("Login finished",python_log)

    # Main selenium loop
    debug("In the main loop",python_log)
    while True:
        if on_off.value == "on":
            browser = getBrowser()
            url_to_visit = all_urls[random.randint(0, len(all_urls))]

            debug("{}.\t{} {}({}) - {}".format(counters["all"], getCurrentTime(), browser, counters[browser],
                                               url_to_visit), python_log)

            if browser == "ff":
                driverFF.get(url_to_visit)
                counters["ff"] = counters["ff"] + 1
            if browser == "chrome":
                driverChrome.get(url_to_visit)
                counters["chrome"] = counters["chrome"] + 1
            if browser == "edge":
                driverEdge.get(url_to_visit)
                counters["edge"] = counters["edge"] + 1

            counters["all"] = counters["all"] + 1

            if time.time() > next_time_long_sleep:
                # Sleep 15-40 minutes periodically
                longSleep = random.randint(15, 40)
                debug("\t{} Long sleep: {} minutes".format(getCurrentTime(), longSleep), python_log)
                time.sleep(longSleep * 60)
                next_time_long_sleep = (time.time()) + (random.randint(45, 70) * 60)
                debug("\t\t{} Next long sleep: in {} minutes".format(getCurrentTime(), str(int(
                    (next_time_long_sleep - time.time()) / 60))), python_log)
            else:
                # Sleep after every request
                shortSleep = random.randint(10, 120)
                debug("\t{} Sleep: {} sec.".format(getCurrentTime(), shortSleep), python_log)
                time.sleep(shortSleep)


def readUrlsFromFile(filename):
    all_urls = []
    with open(filename, "r") as f:
        for url in f.readlines():
            all_urls.append(url.strip())
    return all_urls


def getBrowser():
    rnd = random.randint(1, 100)
    if rnd < 6:  # 5%
        return "edge"
    if 5 < rnd < 16:  # 10%
        return "ff"
    return "chrome"  # 85%


def getDriver(browser):
    if browser == "chrome":
        return webdriver.Chrome()
    if browser == "ff":
        return webdriver.Firefox()
    if browser == "edge":
        return webdriver.Edge()


def loginToOR(driver, environmentUrl):
    driver.get(environmentUrl)
    driver.find_element(By.ID, "EmailAddress").send_keys(OR_USERNAME)
    driver.find_element(By.ID, "Password").send_keys(OR_PASS)
    driver.find_element(By.XPATH, '//button[contains(text(), "Sign in")]').click()
    pass


def getEnvironmentFromUrl(url):
    if url.startswith("https://securetest-a.ownerrez.com") \
            or url.startswith("https://securetest-a.ownerreservations.com") \
            or url.startswith("https://apptest-a.ownerrez.com"):
        return "a"
    elif url.startswith("https://securetest-b.ownerrez.com") \
            or url.startswith("https://securetest-b.ownerreservations.com") \
            or url.startswith("https://apptest-b.ownerrez.com"):
        return "b"
    elif url.startswith("https://securetest-c.ownerrez.com") \
            or url.startswith("https://securetest-c.ownerreservations.com") \
            or url.startswith("https://apptest-c.ownerrez.com"):
        return "c"
    elif url.startswith("https://securetest-d.ownerrez.com") \
            or url.startswith("https://securetest-d.ownerreservations.com") \
            or url.startswith("https://apptest-d.ownerrez.com"):
        return "d"
    elif url.startswith("https://securetest-e.ownerrez.com") \
            or url.startswith("https://securetest-e.ownerreservations.com") \
            or url.startswith("https://apptest-e.ownerrez.com"):
        return "e"
    elif url.startswith("https://securetest-prod.ownerrez.com") \
            or url.startswith("https://securetest-prod.ownerreservations.com") \
            or url.startswith("https://apptest-prod.ownerrez.com"):
        return "prod"
    elif url.startswith("https://securestage.ownerrez.com") \
            or url.startswith("https://securestage.ownerreservations.com") \
            or url.startswith("https://appstage.ownerrez.com"):
        return "stage"
    else:
        return "non-or"



@app.route('/', methods=['GET'])
def index():
    return render_template('body.html')


@app.route('/get-toggle-state', methods=['GET'])
def togglestate():
    return onOff.value


@app.route('/kb.html', methods=['GET'])
def changeOnOffToggleState():
    state = request.args.get('checked')
    if state == 'true':
        onOff.value = "on"
    else:
        onOff.value = "off"

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.errorhandler(werkzeug.exceptions.NotFound)
def handle_bad_request(e):
    return 'Four o four ! (404)', 404


@app.route('/python-log', methods=['GET'])
def python_log():
    return render_template('python-log.html',  logs=python_log)

@app.route('/current-window', methods=['GET'])
def current_window():
    #todo: find current window here based on os and return it instead of dummy return
    return render_template('current-window.html',  window="some window")

if __name__ == '__main__':
    mgr = Manager()
    # Sending this variable to thread.
    onOff = mgr.Value(str, "off")
    python_log=mgr.list([])
    P1 = Process(target=loop, args=(onOff,python_log,))
    P1.start()
    app.run(port=8088, host="0.0.0.0", use_reloader=False, )

