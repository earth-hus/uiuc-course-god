# UIUC COURSE GOD
# course registration cheat for UIUC
# support multiple crn for different courses
# author: Tianhao Chi
# usage: python run.py semester netid password crn1 crn2 ...
# use semester in this format: YYYY-spring, YYYY-summer, YYYY-fall. Example: 2021-spring
# note: do not log in into the system by yourself while using this program

# required package: bs4, selenium, chromedriver

from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import sys

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2


def construct_term_in(semester):
    # This is dark magic.
    year = semester[:semester.find('-')]
    season = semester[semester.find('-')+1:]
    if season == 'winter':
        season_num = 0
    if season == 'spring':
        season_num = 1
    if season == 'summer':
        season_num = 5
    if season == 'fall':
        season_num = 8
    return 120000 + int(str(year)[-2:])*10 + season_num


def get_remaining_seat(soup, cross_list):
    if cross_list:
        try:
            # for cross list courses
            remaining_seat = soup('th', attrs={'scope': 'row'})[
                3].find_next_siblings('td')[2].string
        except IndexError:
            remaining_seat = soup('th', attrs={'scope': 'row'})[
                1].find_next_siblings('td')[2].string
    else:
        remaining_seat = soup('th', attrs={'scope': 'row'})[
            1].find_next_siblings('td')[2].string
    return int(remaining_seat)


def refresh_course_website(driver, crn_arr, cross_list, term_in):
    remaining_seat = 0
    print("start refreshing ...")
    # keep refreshing until find empty space
    while True:
        for crn in crn_arr:
            # this link needs to be updated each semester!
            url = 'https://ui2web1.apps.uillinois.edu/BANPROD1/bwckschd.p_disp_detail_sched?term_in=%d&crn_in=%s' % (
                term_in, crn)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            remaining_seat = get_remaining_seat(soup, cross_list)
            if remaining_seat > 0:
                print("refreshing done!")
                return crn


def register(driver, crn):
    # register single course
    crn_blank = driver.find_element(By.ID, "crn_id1")
    crn_blank.send_keys(crn)
    driver.find_element(By.XPATH, "//input[@value='Submit Changes']").click()
    driver.save_screenshot('screen.png')


def log_in(username, password, driver):
    driver.get(login_url)
    user_field = driver.find_element("name", "USER")
    password_field = driver.find_element("name", "PASSWORD")
    user_field.send_keys(username)
    password_field.send_keys(password)
    driver.find_element("name", "BTN_LOGIN").click()
    return driver


# Semester needs to be updated each semester!
def navigate(driver, username, password, crn):
    year = semester[:semester.find('-')]
    season = semester[semester.find('-')+1:]
    season = season[0].capitalize() + season[1:]
    semester_str = season + ' ' + year + ' - Urbana-Champaign'

    # this url might need update
    url = "https://ui2web1.apps.uillinois.edu/BANPROD1/twbkwbis.P_GenMenu?name=bmenu.P_StuMainMnu"
    driver.get(url)
    driver.find_element('link text', 'Classic Registration').click()
    driver.find_element('link text', 'Add/Drop Classes').click()
    driver.find_element('link text', 'I Agree to the Above Statement').click()

    # go to register page
    options = Select(driver.find_element(By.ID, 'term_id'))
    options.select_by_visible_text(semester_str)
    path = '//input[@type="submit" and @value="Submit"]'
    driver.find_element(By.XPATH, path).click()

# ============================================ main ===================================


# put the crn numbers into the array
crn_arr = []
for i in range(4, len(sys.argv)):
    crn_arr.append(sys.argv[i])
if len(crn_arr) < 1:
    print("crn index error")

# login url may change and might need update in the future
login_url = 'https://login.uillinois.edu/auth/SystemLogin/sm_login.fcc?TYPE=33554433&REALMOID=06-e5b1520c-d10f-419a-bce9-a59c4292488e&GUID=&SMAUTHREASON=0&METHOD=GET&SMAGENTNAME=-SM-J9ldxGzDajRVOCvCtHkKc2Pex3VVR3ifECA%2b1KBtU5c%2fEIF8mWDOJjqUJhESA8EV&TARGET=-SM-HTTPS%3a%2f%2flogin%2euillinois%2eedu%2faffwebservices%2fafflogin%2fsdnp%2fredirect%2ejsp%3fSPID%3dhttps-%3A-%2F-%2Feis%2eapps%2euillinois%2eedu-%2Fbanner%26SAMLRequest%3djZFLb8IwEITv-%2FRWR7-%2BRFCKlFglAREhKVEI8eeqkcZwFLjp16bdqfX0MbFfVSjivtzOx-%2BM5l-%2BtjI4g0GhVUmSMCYBKK4boY4l2e8Wg4JMq4cJslZ2dObsSW3g3QHaYIYIxnrZk1boWjBbMGfBYb9ZleRkbYc0ikBgyLoOQyekFEr7ERoXcd22WjFvR4K5NxOK2esBvU7qo1B-%2FROxw-%2BIAav1Mw6lwtBY8ul6WIerpdL-%2BflP7k1UwoMCRbacLh-%2BU5IDkwgk8GLyxgtW5zzO05xBHQMvCp5ko6SJ-%2BXAYN-%2BPcr-%2BGaIYoz-%2FAoRHSwVWqZsSdI4zQbxeBCPdklBk4xmwzB9HL2S4KWHnF4ge-%2BwK6RVrSZxRVDMUSBVrAanldDt7XlG-%2FSTujreZakuqnhGueud-%2BA9T2R6i46k-%2Bg2p-%2BrH2-%2B6rLw-%3D-%3D%26RelayState%3def8234db--ae82--4021--bb12--33df0f18161b%26SigAlg%3dhttp-%3A-%2F-%2Fwww%2ew3%2eorg-%2F2000-%2F09-%2Fxmldsig-%23rsa--sha1%26Signature%3dSdLHy6JnG02fs9tHO8zuSS9-%2F56XcpCRbuqPuypd8n7AJSEAvRVgA2o0TPIvy08gMrGGF9wq2OiGI5qQIqiqwFN2L3vFARskP2P294Z4A-%2FQh-%2FYa3soT8Lgu9uADoZvrGSpS-%2F9CsIE59nmHOftt2FSuuxbMte-%2BwbYThylIBGV-%2Bo9fg-%2Bft6u6PazxuFQL2-%2BgQ8FK6ZKlrgUedvkfufvRPvWyKI6HuuRlb4v-%2FG835zYIEgRIraWJQtygLIjiR5PeoWpiSUae1292HXzvvtGJ8Uslql7lQZW4eLfo8CkzJ96ELPvjasSLTkhmF9KtOCuZkLjWT2PPtUE1C8Bsk8oeAy-%2BYNQ-%3D-%3D%26SMPORTALURL%3dhttps-%3A-%2F-%2Flogin%2euillinois%2eedu-%2Faffwebservices-%2Fpublic-%2Fsaml2sso'

# semester in this format: YYYY-spring/YYYY-summer/YYYY-fall
semester = sys.argv[1]
username = sys.argv[2]  # netid
password = sys.argv[3]  # password

# please change to true if the course is crosslisted
cross_list = False

start = time.time()

term_in = construct_term_in(semester)

while len(crn_arr) != 0:
    # the driver for refresh
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver = log_in(username, password, driver)
    crn_success = ""
    crn_success = refresh_course_website(driver, crn_arr, cross_list, term_in)

    # if empty seat found. the driver for register
    navigate(driver, username, password, crn_success)
    register(driver, crn_success)

    msg = "time spent: %s" % (time.time() - start)
    print(msg)
    print("crn: " + str(crn_success) + " is done!!!!!!!!!!!!!!!!!")
    crn_arr.remove(crn_success)
    driver.quit()
