# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 14:55:03 2022

Web Scraping - get data from HK Jockey Club
@author: tomfoolc

Date                Version         Remarks
-------------       ---------       ------------------------
2023-Apr-17         v1.0            1st completed version
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

#from datetime import date
import time
import datetime

import csv

#################################
# define constant variable
#################################
_BraveBrowserPath = r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'
_HkjcRaceResultUrl = r'https://racing.hkjc.com/racing/information/Chinese/Racing/LocalResults.aspx'
_HkjcRaceResultRaceDateParam = r'?RaceDate='
_HkjcRaceResultRaceNoParam = r'&RaceNo='
_StartYear = '2022'
_StartMonth = '01'
_StartDay = '01'
_EndYear = '2022'
_EndMonth = '03'
_EndDay = '31'

#################################
# define function
#################################
#get the URL of HJKC race result page
def getHkjcRaceResultUrl(_raceYear='', _raceMonth='', _raceDay='', _raceNo=''):
    url = _HkjcRaceResultUrl
    if (_raceYear != '' and _raceMonth != '' and _raceDay != ''):
        url += f'{_HkjcRaceResultRaceDateParam}{_raceYear}/{raceMonth}/{raceDay}'
    
    if (_raceNo != ''):
        url += f'{_HkjcRaceResultRaceNoParam}{_raceNo}'

    return url

def getBs4fromPage(_raceYear, _raceMonth, _raceDay, _raceNo, _chrome):
    _chrome.get(getHkjcRaceResultUrl(_raceYear, _raceMonth, _raceDay, _raceNo,))
    WebDriverWait(_chrome, 120).until(EC.visibility_of_element_located((By.XPATH, r"//*[@id='footer']"))) #passing tuple to visibility_of_element_located
    soup = BeautifulSoup(_chrome.page_source, 'html.parser')

    time.sleep(20)

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

    return int(tmp_str)

#get race information
def getRaceInfo(_raceData, _soup):
    #define list and dictionary for venue, class and condition
    venueDict = {"沙田:":"ST", "跑馬地:":"HV"}
    classListInChi = ["第一班", "第二班", "第三班", "第四班", "第五班"]
    conditionDict = {
        "快地":"Firm", "好地至快地":"Good To Firm", "好地":"Good", "好地至黏地":"Good To Yielding",
        "黏地":"Yielding", "黏地至軟地":"Yielding To Soft", "軟地":"Soft", "大爛地":"Heavy",
        "濕快地":"Wet fast", "慢地":"Slow", "濕慢地":"Wet slow", "受天雨影響":"Rain affected", 
        "例常灑水":"Normal watering"
        }

    #find the tags for getting race info
    raceVenueSpanTags = _soup.select('td.font_w7.f_tar span')
    raceTabDivTdTags = _soup.select('div.race_tab td')

    #init the value to the dictionary
    _raceData["venue"] = ""
    _raceData["course"] = ""
    _raceData["distance"] = 0
    _raceData["going"] = ""
    _raceData["class"] = ""

    #venue: ST / HV / NA
    _raceData["venue"] = venueDict.get(raceVenueSpanTags[0].text,"NA") if (len(raceVenueSpanTags) > 0) else "NA"
    
    #loop for the course, distance, class and going
    for tmp_td_tag in raceTabDivTdTags:
        if (tmp_td_tag.text == "全天候跑道"):
            _raceData["course"] = "AWT"
        elif (tmp_td_tag.text.find("草地")>=0):
            _raceData["course"] = tmp_td_tag.text[tmp_td_tag.text.index("\"")+1:tmp_td_tag.text.index("\" 賽道")]
        elif (tmp_td_tag.text.find("第")>=0 and tmp_td_tag.text.find("班")>=0):
            _raceData["distance"] = int(tmp_td_tag.text[6:10])
            _raceData["class"] = classListInChi.index(tmp_td_tag.text[0:3])+1
        elif (tmp_td_tag.text in conditionDict):
            _raceData["going"] = conditionDict[tmp_td_tag.text]

    return _raceData

#get race information
def getRaceResult(_raceId, _soup):
    placeConditionList = [
        "DISQ", "DNF", "FE", "PU", "TNP", "UR", "VOID", "WR", "WV", 
        "WV-A", "WX", "WX-A", "WXNR"]
    raceResult = []
    rowNum = 0

    #find the tags for getting race result
    raceResultTrTags = _soup.select('tbody.f_fs12.fontFam tr')

    for row in raceResultTrTags:
        rowNum += 1
        tdTags = row.find_all("td")

        #init value
        place = 0
        horse_no = 0
        horse_name = ""
        horse_id = ""
        jockey_name = ""
        trainer_name = ""
        actual_weight = 0
        draw = 0
        win_odds = 0.0

        for num in range(0,len(tdTags)):
            tmp_str = (tdTags[num].text).replace(u'\xa0','')
            tmp_str = tmp_str.replace('\n','')

            if (num == 0):
                if (tmp_str in placeConditionList):
                    place = -1
                elif (tmp_str.find("平頭馬")>0):
                    tmp_str = tmp_str.replace(" 平頭馬","")
                    place = int(tmp_str)
                else:
                    place = rowNum
            elif (num == 1 and place > 0):
                horse_no = int(tmp_str)
            elif (num == 2 and place > 0):
                horse_name = tmp_str[0: tmp_str.find("(")]
                horse_id = tmp_str[tmp_str.find("(")+1: tmp_str.find(")")]
            elif (num == 3 and place > 0):
                jockey_name = tmp_str
            elif (num == 4 and place > 0):
                trainer_name = tmp_str
            elif (num == 5 and place > 0):
                actual_weight = int(tmp_str)
            elif (num == 7 and place > 0):
                draw = int(tmp_str)
            elif (num == 11 and place > 0):
                win_odds = float(tmp_str)

        #only write the result data when place > 0, otherwise it means the horse give up the race
        if (place > 0):
            raceResultData = {
                "race_id":_raceId, "place":place, "horse_no":horse_no, "horse_name":horse_name,
                "horse_id":horse_id, "jockey_name":jockey_name, "trainer_name":trainer_name,
                "actual_weight":actual_weight, "draw":draw, "win_odds":win_odds
            }

            raceResult.append(raceResultData)
    
    return raceResult

#check if it is Valid Race
def isValidRaceDate(_raceYear, _raceMonth, _raceDay, _soup):
    raceDateSpanTags = _soup.select('span.f_fl.f_fs13')
    raceNoTdTags = _soup.select('tr.bg_blue.color_w.font_wb')

    if (not raceDateSpanTags or not raceNoTdTags):
        return False
    
    if (raceDateSpanTags[0].text.find(f'{_raceDay}/{_raceMonth}/{_raceYear}') <= 0 or 
        raceNoTdTags[0].text.find(r'第 1 場') <= 0):
        return False

    return True

#get Start Time
startTime = datetime.datetime.today()

#########################################
# define Chrome Options and Web Driver
#########################################
#binary_location: Brave Browser location (for opening with Brave Browser)
#add_argument("--disable-notifications"): disable pop-up / notification
options = webdriver.ChromeOptions()
options.binary_location = _BraveBrowserPath
options.add_argument("--disable-notifications")
options.add_argument("--enable-javascript")
options.add_experimental_option('excludeSwitches', ['enable-logging'])


#selenium4 changed to use selenium.webdriver.chrome.service to initial webdriver
#ref: http://pypi.org/project/webdriver-manager
#chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) #Chrome
chrome = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()), chrome_options=options) #Brave

# get Racing Date
soup = getBs4fromPage('', '', '', '', chrome)
raceDateItems = getRaceDate(soup)
#raceDateItems = [r'07/12/2022']
#print(raceDateItems)

raceInfoHeader = [
    "race_year","race_month","race_day","race_date","race_no","race_id","venue","course",
    "distance","going","class"
    ]
raceResultHeader = [
    "race_id","place","horse_no","horse_name","horse_id","jockey_name","trainer_name",
    "actual_weight","draw","win_odds"
    ]

raceInfo = []
raceResult = []

for raceDateElement in reversed(raceDateItems):
    #construct date elements
    raceDay = raceDateElement[:2]
    raceMonth = raceDateElement[3:5]
    raceYear = raceDateElement[6:]
    raceDate = f'{raceYear}{raceMonth.zfill(2)}{raceDay.zfill(2)}'
    startDate = f'{_StartYear}{_StartMonth.zfill(2)}{_StartDay.zfill(2)}'
    endDate = f'{_EndYear}{_EndMonth.zfill(2)}{_EndDay.zfill(2)}'

    #constrain for getting the race info by a start date
    if (raceDate >= startDate and raceDate <= endDate):
        #get last race number
        soup = getBs4fromPage(raceYear, raceMonth, raceDay, '', chrome)
        lastRaceNo = getLastRaceNo(raceYear, raceMonth, raceDay, soup)

        #for each race
        for i in range(1, lastRaceNo+1):
            #construct race info
            raceData = {
                "race_year":raceYear, "race_month":raceMonth, "race_day":raceDay,
                "race_date":raceDate, "race_no":i,"race_id":f'{raceDate}{str(i).zfill(2)}'
            }

            soup = getBs4fromPage(raceYear, raceMonth, raceDay, i, chrome)

            try:
                #get race info
                raceInfo.append(getRaceInfo(raceData, soup))

                #get race result
                raceResult.extend(getRaceResult(f'{raceDate}{str(i).zfill(2)}', soup))
            except Exception as ex:
                print(f'{ex}\r\nRace Date: {raceDate} || Race No: {str(i).zfill(2)}')

if (len(raceInfo) > 0):
    firstDate = raceInfo[0].get("race_date")
    lastDate = raceInfo[len(raceInfo)-1].get("race_date")
    raceInfoFileName = f'./race_info_{firstDate}_{lastDate}.csv'
    raceResultFileName = f'./race_result_{firstDate}_{lastDate}.csv'

    with open(raceInfoFileName,"a",encoding="UTF8",newline="") as f:
        writer = csv.DictWriter(f, fieldnames=raceInfoHeader)

        if (len(raceInfo) > 0):
            writer.writeheader()
            writer.writerows(raceInfo)

    with open(raceResultFileName,"a",encoding="UTF8",newline="") as f:
        writer = csv.DictWriter(f, fieldnames=raceResultHeader)

        if (len(raceResult) > 0):
            writer.writeheader()
            writer.writerows(raceResult)

#get End Time
endTime = datetime.datetime.today()
processTime = (endTime - startTime).total_seconds() / 60
print(f'[Web Scraping Completed for racing date {firstDate} to {lastDate}]')
print(f'[Start from {startTime}]')
print(f'[End from {endTime}]')
print(f'[Process Time {processTime} minutes]')
print(f'[No. of Racing {len(raceInfo)}]')