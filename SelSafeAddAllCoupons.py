import csv
import datetime

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

import time

def getLogin(browser):
    browser.get("https://safeway.com/content/www/safeway/en/account/sign-in.html")

def formatAccount(account):
    return account.split(':')

def findAndLogin(username, password, browser):
    browser.find_element_by_id('label-email').send_keys(username)
    browser.find_element_by_id('label-password').send_keys(password, Keys.ENTER)

def logOut(browser):
    browser.execute_script('SWY.OKTA.signOut(event);')
    time.sleep(2)

def handleNewStore(browser):
    browser.find_element_by_class_name('keep-store-btn').click()
    time.sleep(2)

# Main method
COUPONS_URL = 'https://www.safeway.com/justforu/coupons-deals.html'
account_file = open('./accounts.txt', 'r')
account_list = []
options = Options()
options.headless = True

browser = webdriver.Firefox(options=options)

result_dict = {}

for line in account_file:
    try:
        counter = 0
        username, password = formatAccount(line)
        getLogin(browser)
        time.sleep(2)
        findAndLogin(username, password, browser)
        time.sleep(3)
        browser.get(COUPONS_URL)
        time.sleep(2)

        while True:
            try:
                load_more = browser.find_element_by_css_selector('button.load-more')
                try:
                    load_more.click()
                except ElementClickInterceptedException:
                    handleNewStore(browser)
                    continue
                time.sleep(0.5)
            except NoSuchElementException:
                break
        button_array = browser.find_elements_by_css_selector('button.grid-coupon-btn')
        for button in button_array:
            try:
                button.click()
                time.sleep(0.1)
                counter += 1
            except ElementClickInterceptedException:
                browser.find_element_by_id('boxtopModalCancelBtn').click()
                time.sleep(1)
                button.click()
                time.sleep(0.1)
                counter += 1
        print('{} : {}'.format(username, counter))
        result_dict[username] = counter
        logOut(browser)
        time.sleep(3)
            
    except KeyboardInterrupt:
        print("Caught keyboard interupt, recording data so far")
        break
    except Exception as e:
        print(f'Exception caught while processing {username}')
        print(e)

browser.quit()
account_file.close()

csv_date = datetime.datetime.now().strftime('%m_%d_%Y_%I-%M%p')
with open('./CouponStats/Coupon_Results_%s.csv' % csv_date, 'w') as csvfile:
    wcsv = csv.writer(csvfile, lineterminator='\n')
    csv_fields = ['Username', 'Coupon#']
    wcsv.writerow(csv_fields)
    for account, counters in result_dict.items():
        wcsv.writerow([account, counters])