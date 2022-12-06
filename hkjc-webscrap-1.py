# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 14:55:03 2022

Web Scraping - get data from HK Jockey Club
@author: tomfoolc
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By


import time

#define Chrome Options
#binary_location: Brave Browser location (for opening with Brave Browser)
#add_argument("--disable-notifications"): diable pop-up / notification
options = webdriver.ChromeOptions()
options.binary_location = r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'
options.add_argument("--disable-notifications")

#driver is placed on the upper folder and named as chromedriver108
#selenium4 changed to use selenium.webdriver.chrome.service to initial webdriver
#ref: http://pypi.org/project/webdriver-manager
#chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) #Chrome
chrome = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()), options=options) #Brave

chrome.get("https://racing.hkjc.com/racing/information/Chinese/Racing/LocalResults.aspx")

time.sleep(3)

raceDateList = chrome.find_element(By.ID, "selectId")
raceDateItems = raceDateList.find_elements(By.TAG_NAME, "option")

for raceDateItem in raceDateItems:
    raceDate = raceDateItem.text
    print(f'raceDate: {raceDate}')

print(f'Completed test')