# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 14:55:03 2022

Web Scraping - get data from HK Jockey Club
@author: tomfoolc
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager
import time

#define Chrome Options
#binary_location: Brave Browser location (for opening with Brave Browser)
#add_argument("--disable-notifications"): diable pop-up / notification
options = webdriver.ChromeOptions()
options.binary_location = r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'
options.add_argument("--disable-notifications")

#driver is placed on the upper folder and named as chromedriver108
#chrome = webdriver.Chrome('../driver/chromedriver108', options=options)
chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

chrome.get("https://racing.hkjc.com/racing/information/Chinese/Racing/LocalResults.aspx")
#chrome.get("http://www.yahoo.com")

time.sleep(3)
#print(chrome.page_source)

raceDateList = chrome.find_element(By.ID, "selectId")
raceDateItems = raceDateList.find_elements(By.TAG_NAME, "option")

for raceDateItem in raceDateItems:
    raceDate = raceDateItem.text
    print(f'raceDate: {raceDate}')

print(f'Completed test')