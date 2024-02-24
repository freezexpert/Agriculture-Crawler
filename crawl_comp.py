from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from fake_useragent import UserAgent
import pandas as pd
import time
from random import randint
import logging
def crwal_table():
    tbl = driver.find_element(By.XPATH, '/html/body/div/form/div/table').get_attribute('outerHTML')
    a = pd.read_html(tbl)
    df = pd.concat(a, ignore_index=True)
    df.columns = ['縣市鄉鎮名稱', '種植面積(公頃)', '收穫面積(公頃)', '每公頃收量(公斤)', '收量(公斤)']

    # df['年份'] =  driver.find_element(By.XPATH, '/html/body/div/table[2]/tbody/tr/td[1]').text[3:]
    df['年份'] = year
    df['作物'] = driver.find_element(By.XPATH, '/html/body/div/table[2]/tbody/tr/td[3]').text[3:]
    column_order = ['年份', '作物'] + [col for col in df.columns if col != '年份' and col != '作物']
    df = df[column_order]
    return df[2:-1]

def has_record(crop, city):
    if city[0] == '臺':
        city = '台' + city[1:]
    # print(crop, city)
    cond1 = crawl_df['作物'].str.contains(crop)
    cond2 = crawl_df['縣市鄉鎮名稱'].str.contains(city)
    sub_df = crawl_df[cond1 & cond2]
    if sub_df.empty:
        return False
    else: 
        # print('find record')
        return True
    
def is_blocked():
    year_select.select_by_value('111')
    select.select_by_index(3)
    crop_select.select_by_index(0)
    city_select.select_by_index(0)
    time.sleep(1)
    submit = driver.find_element(By.NAME, 'btnSend').click()
    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/form/div/table')))
    test = crwal_table()
    time.sleep(1)
    if test.empty:
        print('blocked')
        driver.back()
        return True
    else:
        print('finished')
        driver.back()
        return False

logging.basicConfig(filename='check.log', encoding='utf-8', level=logging.INFO)
url = 'https://agr.afa.gov.tw/afa/pgcroptown_cond.jsp'
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option("detach", True)
# options.add_argument('--headless')
ua = UserAgent()
options.add_argument(f"user-agent={ua.random}")
driver = webdriver.Chrome(options=options)
driver.get(url)
city_selector = driver.find_element(By.NAME, 'city')
city_select = Select(city_selector)
cities = city_select.options
year_selector = driver.find_element(By.NAME, 'accountingyear')
year_select = Select(year_selector)
years = year_select.options
all_df = []
crawl_df = []
flag = False
wait = WebDriverWait(driver, 10)
missing = [94]
# missing = range(86, 102)
for j in cities[21:22]:
    city_select.select_by_visible_text(j.text)
    for year in missing:
        if year < 100:
            year = '0' + str(year)
        else: 
            year = str(year)
        all_df = []
        crawl_df = pd.read_csv(f'{year}.csv')
        # print(crawl_df)
        for k in range(2, 4):
            selector = driver.find_element(By.NAME, 'corn001')
            select = Select(selector)
            select.select_by_index(k)
            crop_selector = driver.find_element(By.NAME, 'crop')
            crop_select = Select(crop_selector)
            if k == 2:
                crops = crop_select.options
                for u in range(8, 13): 
                    if has_record(crops[u].text[4:], j.text[3:]):
                        continue
                    # 8~12
                    # print(u, k)
                    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/form/div/table/tbody/tr[1]/td[2]/select')))
                    year_select.select_by_value(year)
                    select.select_by_index(k)
                    crop_select.select_by_index(u)
                    time.sleep(1)
                    submit = driver.find_element(By.NAME, 'btnSend').click()
                    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/form/div/table')))
                    all_df.append(crwal_table())
                    time.sleep(1)
                    driver.back()
            elif k == 3:
                crops = crop_select.options
                for u in crops:
                    if has_record(u.text[4:], j.text[3:]):
                        continue
                    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/form/div/table/tbody/tr[1]/td[2]/select')))
                    year_select.select_by_value(year)
                    select.select_by_index(k)
                    crop_select.select_by_visible_text(u.text)
                    # sec = randint(1, 5)
                    sec = 1
                    time.sleep(sec)
                    submit = driver.find_element(By.NAME, 'btnSend').click()
                    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/form/div/table')))
                    all_df.append(crwal_table())
                    # sec = randint(1, 5)
                    sec = 3
                    time.sleep(sec)
                    driver.back()
        final_df = pd.concat(all_df, ignore_index=True)
        final_df.to_csv(f'{year}_{j.text}comp.csv',index=False)
        if is_blocked():
            print(f'{year}_{j.text} has been blocked')
            logging.info(f'{year}_{j.text} has been blocked')
            time.sleep(5400)
        city_select.select_by_visible_text(j.text)
driver.quit()