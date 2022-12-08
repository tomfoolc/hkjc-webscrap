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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

from datetime import date
import time

import csv

#################################
# define constant variable
#################################
_BraveBrowserPath = r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'
_HkjcRaceResultUrl = r'https://racing.hkjc.com/racing/information/Chinese/Racing/LocalResults.aspx'
_HkjcRaceResultRaceDateParam = r'?RaceDate='
_HkjcRaceResultRaceNoParam = r'&RaceNo='
_StartYear = '2021'
_StartMonth = '07'
_StartDay = '01'

#################################
# define function
#################################
#get the URL of HJKC race result page
def getHkjcRaceResultUrl(_raceYear='', _raceMonth='', _raceDay='', _raceNo=''):
    url = _HkjcRaceResultUrl
    if (_raceYear != '' and _raceMonth != '' and _raceDay != ''):
        url += _HkjcRaceResultRaceDateParam + _raceYear + r'/' + _raceMonth + r'/' + _raceDay
    
    if (_raceNo != ''):
        url += _HkjcRaceResultRaceNoParam + _raceNo

    return url

def getBs4fromPage(_raceYear, _raceMonth, _raceDay, _raceNo, _chrome):
    _chrome.get(getHkjcRaceResultUrl(_raceYear, _raceMonth, _raceDay, _raceNo,))
    WebDriverWait(_chrome, 120).until(EC.visibility_of_element_located((By.XPATH, r"//*[@id='footer']"))) #passing tuple to visibility_of_element_located
    soup = BeautifulSoup(_chrome.page_source, 'html.parser')

    return soup

#get the racing date
def getRaceDate(_soup):
    raceDateItems = []

    raceDateList = _soup.select('select#selectId') #extract select element with id selectId

    if (len(raceDateList) > 0):
        raceDateOptionTags = raceDateList[0].find_all('option') #find all option element 
        for optionTag in raceDateOptionTags:
            raceDateItems.append(optionTag.text)

    return raceDateItems

#get last race no
def getLastRaceNo(_raceYear, _raceMonth, _raceDay, _soup):
    if (not isValidRaceDate(_raceYear, _raceMonth, _raceDay, _soup)):
        return -1

    raceNoParentTags = _soup.select('table.f_fs12.js_racecard')
    if (not raceNoParentTags):
        return -2

    raceNoImgTags = raceNoParentTags[0].find_all('img')
    if (not raceNoImgTags):
        return -3

    raceNoFindAll = False
    for raceNoImgTag in reversed(raceNoImgTags):
        if (raceNoFindAll):
            imgTagStr = raceNoImgTag['src']
            gifExtPos = imgTagStr.find('.gif')
            tmp_str = imgTagStr[gifExtPos-2:gifExtPos]
            if (tmp_str[0] == '_'):
                tmp_str = tmp_str[1:2]
            
            break

        if (raceNoImgTag['src'].find('racecard_rt_all.gif')) > 0:
            raceNoFindAll = True

    return tmp_str

#check if it is Valid Race
def isValidRaceDate(_raceYear, _raceMonth, _raceDay, _soup):
    raceDateSpanTags = _soup.select('span.f_fl.f_fs13')
    raceNoTdTags = _soup.select('tr.bg_blue.color_w.font_wb')

    #print(raceDateSpanTags)
    #print(raceNoTdTags)
    if (not raceDateSpanTags or not raceNoTdTags):
        return False
    
    if (raceDateSpanTags[0].text.find(f'{_raceDay}/{_raceMonth}/{_raceYear}') <= 0 or 
        raceNoTdTags[0].text.find(r'第 1 場') <= 0):
        return False

    return True

#########################################
# define Chrome Options and Web Driver
#########################################
#binary_location: Brave Browser location (for opening with Brave Browser)
#add_argument("--disable-notifications"): disable pop-up / notification
options = webdriver.ChromeOptions()
options.binary_location = _BraveBrowserPath
options.add_argument("--disable-notifications")
options.add_argument("--enable-javascript")

#selenium4 changed to use selenium.webdriver.chrome.service to initial webdriver
#ref: http://pypi.org/project/webdriver-manager
#chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) #Chrome
chrome = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()), chrome_options=options) #Brave

##################
# get Racing Date
##################
soup = getBs4fromPage('', '', '', '', chrome)
#raceDateItems = getRaceDate(soup)
raceDateItems = [r'07/12/2022']
#print(raceDateItems)

header = ["RaceYear","RaceMonth","RaceDay","LastRaceNo"]
data = []
with open(r"./race_list"+date.today().strftime(r'%y%m%d')+".csv","a",encoding="UTF8",newline="") as f:
    writer = csv.DictWriter(f, fieldnames=header)

    for raceDate in raceDateItems:
        raceDay = raceDate[:2]
        raceMonth = raceDate[3:5]
        raceYear = raceDate[6:]

        if (f'{raceYear}{raceMonth.zfill(2)}{raceDay.zfill(2)}' > f'{_StartYear}{_StartMonth.zfill(2)}{_StartDay.zfill(2)}'):
            soup = getBs4fromPage(raceYear, raceMonth, raceDay, '', chrome)
            lastRaceNo = getLastRaceNo(raceYear, raceMonth, raceDay, soup)

        data.append({"RaceYear":raceYear, "RaceMonth":raceMonth, "RaceDay":raceDay, "LastRaceNo":lastRaceNo})

    if (len(data) > 0):
        writer.writeheader()
        writer.writerows(data)

#soup = getBs4fromPage('2022', '11', '02', '', chrome)
#isValidRaceDate('2022', '11', '02', soup)
#lastRaceNo = getLastRaceNo('2022', '11', '01', chrome)

#chrome.get(getHkjcRaceResultUrl('2022','12','07'))
#soup = BeautifulSoup(chrome.page_source, 'html.parser')
#time.sleep(30)
#print(isValidRaceDate('2022','12','07', soup))


# To-do
# 1. assemble the race date and get the race result page
# 2. cross check the race date with the input race date (div.raceMeeting_select > span.f_fl.f_fs13) and check raceno (div.localResults.commContent.fontFam > tr.bg_blue.color_w.font_wb)
# 3. cross check with the input date for stopping the web scraping
# 4. determine valid racing result
# 4.1 exclude Typhoon day (2-Nov-2022) 
# 4.2 exclude non-HK racing (1-Nov-2022) (no span.ff_fl.f_fs13 under div.raceMeeting_select)
#

print(f'Completed test')