import csv
from selenium import webdriver
import pandas as pd
import os as os
import time
import subprocess
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support import expected_conditions as ec

def reader(file_name):
    with open(file_name, encoding='utf-8', errors="ignore") as f:
        reader_data = csv.reader(f, delimiter=',')
        for row in reader_data:
            yield row

script_path = os.getcwd()
os.chdir(script_path + "\\Results")

txt_reader = reader("new21.csv")
first_line = next(txt_reader)
col_count = len(first_line)
data = []



"""Парсинг страницы с должниками"""
def parser_main_page(driver, inn):
    person = inn
    try:
        fisic = driver.find_element_by_id('ctl00_cphBody_rblDebtorType_1')
        fisic.click()
        time.sleep(10)
        INN = driver.find_element_by_id('ctl00_cphBody_PersonCode1_CodeTextBox')
        INN.clear()
        INN.send_keys(person)
        btn_search = driver.find_element_by_id('ctl00_cphBody_btnSearch')
        btn_search.click()
        time.sleep(10)
        person = driver.find_element_by_xpath("//table[@id='ctl00_cphBody_gvDebtors']/tbody/tr[2]/td[2]/a")
    except NoSuchElementException as e:
        person = None
    return person


"""Парсинг личной страницы должника"""
def parser_person_page(driver, person_url):
    driver1.set_page_load_timeout(10)
    driver.get(person_url)
    find_urls = []
    inn = driver.find_element_by_id('ctl00_cphBody_lblINN').text
    #snils = driver.find_element_by_id('ctl00_cphBody_lblSNILS').text
    messages = driver.find_elements_by_xpath("//table[@id='ctl00_cphBody_gvMessages']/tbody/tr[position() > 1]")
    for message in messages:
        url = message.find_element_by_tag_name('a').get_attribute('href')
        find_urls.append(url)
    return inn, find_urls


chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_experimental_option('excludeSwitches',['enable-logging'])
#chromeOptions.add_argument('headless')
#chromeOptions.add_argument('window-size=1200x600') # optional
#print(driver.title)
#print(driver.current_url)
result = pd.DataFrame(columns=['FULLNAME', 'INN', 'SNILS', 'DOCUMENT', 'DATE'])

driver1 = webdriver.Chrome("C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe",
                           options=chromeOptions)
i = 1
for line in txt_reader:
    #print(line[0])
    driver1.set_page_load_timeout(30)
    driver1.get("https://bankrot.fedresurs.ru/DebtorsSearch.aspx")
    #time.sleep(5)
    person = parser_main_page(driver1, line[0])
    if person is None:
        print(f"{line[0]} не найден")
        continue
    name = person.text # ФИО должника
    person_url = person.get_attribute('href') # Ссылка на личную страницу
    #print(f"{name} {person_url}")
    inn, loop = parser_person_page(driver1, person_url)
    for item in loop:
        try:
            driver1.set_page_load_timeout(5)
            driver1.get(item)
        except WebDriverException as w:
            print(f"{line[0]} не просмотрен до конца")
            continue
        data_item = {}
        tables = driver1.find_elements_by_class_name('headInfo')
        #print(type(tables[0]))
        important_message = tables[0].find_element_by_class_name('even')
        ff = important_message.find_elements_by_tag_name('td')[1]
        #print(ff.text)
        try:
            if 'о признании гражданина банкротом и введении реализации имущества гражданина' in ff.text :
                #important_date = driver1.find_element_by_xpath("//table[@class='headInfo']/tbody/tr[3]/td[2]").text
                important_date = tables[0].find_elements_by_class_name('even')[1]
                date = important_date.find_elements_by_tag_name('td')[1].text
                #important_date = tables[0].find_elements_by_class_name('primary')
                important_doc = tables[1].find_elements_by_tag_name('tr')[-1]
                doc = important_doc.find_elements_by_tag_name('td')[1].text
                data_item['FULLNAME'] = name
                data_item['INN'] = inn
                data_item['SNILS'] = line[0]
                data_item['DOCUMENT'] = doc
                data_item['DATE'] = date
                result = result.append(data_item, ignore_index=True)
                print(f"{i},{data_item['FULLNAME']},{data_item['INN']},{data_item['SNILS']},{data_item['DOCUMENT']},{data_item['DATE']}")
        except:
            continue
    person = None

    if i == 10:
        driver1.quit()
        #subprocess.call("TASKKILL /f /IM CHROME.EXE")
        #subprocess.call("TASKKILL /f /IM CHROMEDRIVER.EXE")
        time.sleep(60)
        i = 0
        driver1 = webdriver.Chrome("C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe", options=chromeOptions)
    i += 1

driver1.quit()
result.to_csv('result.csv', index=False, encoding='utf-8-sig')
