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

#from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

import time

#################################
# define constant variable
#################################
_BraveBrowserPath = r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'
_HkjcRaceResultUrl = r'https://racing.hkjc.com/racing/information/Chinese/Racing/LocalResults.aspx'
_HkjcRaceResultRaceDateParam = r'?RaceDate='
_HkjcRaceResultRaceNoParam = r'&RaceNo='

#################################
# define function
#################################
#get the URL of HJKC race result page
def getHkjcRaceResultUrl(raceYear=0, raceMonth=0, raceDay=0, raceNo=0):
    url = _HkjcRaceResultUrl
    if (raceYear != 0 and raceMonth != 0 and raceDay != 0 and raceNo != 0):
        url += _HkjcRaceResultParam + raceYear + r'/' + raceMonth + r'/' + raceDay + _HkjcRaceResultRaceDateParam + raceNo
    return url

#get the racing date
def getRaceDate(_chrome):
    raceDateItems = []
    
    _chrome.get(getHkjcRaceResultUrl()) #get the init page
    soup = BeautifulSoup(chrome.page_source, 'html.parser')

    raceDateList = soup.select('#selectId') #select the code with id=selectId

    if (len(raceDateList) > 0):
        raceDateItems = raceDateList[0].findAll('option')

    return raceDateItems


#########################################
# define Chrome Options and Web Driver
#########################################
#binary_location: Brave Browser location (for opening with Brave Browser)
#add_argument("--disable-notifications"): disable pop-up / notification
options = webdriver.ChromeOptions()
options.binary_location = _BraveBrowserPath
options.add_argument("--disable-notifications")

#selenium4 changed to use selenium.webdriver.chrome.service to initial webdriver
#ref: http://pypi.org/project/webdriver-manager
#chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) #Chrome
chrome = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()), options=options) #Brave

##################
# get Racing Date
##################
raceDateItems = getRaceDate(chrome)

# To-do
# 1. assemble the race date and get the race result page
# 2. cross check the race date with the input race date
# 3. cross check with the input date for stopping the web scraping
# 4. determine valid racing result
# 4.1 exclude Typhoon day (2-Nov-2022) 
# 4.2 exclude non-HK racing (1-Nov-2022)
#


for raceDateItem in raceDateItems:
    raceDate = raceDateItem.text
    print(f'raceDate: {raceDate}')

print(f'Completed test')