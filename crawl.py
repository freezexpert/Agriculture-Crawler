from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from fake_useragent import UserAgent
import pandas as pd
import time
city_list = ['01']
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
year = '089'
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
    # df = df[2:-1]
    
    return df[2:-1]

wait = WebDriverWait(driver, 10)

for j in cities:
    city_select.select_by_visible_text(j.text)
    for k in range(2, 4):
        selector = driver.find_element(By.NAME, 'corn001')
        select = Select(selector)
        select.select_by_index(k)
        crop_selector = driver.find_element(By.NAME, 'crop')
        crop_select = Select(crop_selector)
        if k == 2:
            for u in range(8, 13): 
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
                wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/form/div/table/tbody/tr[1]/td[2]/select')))
                year_select.select_by_value(str(year))
                select.select_by_index(k)
                crop_select.select_by_visible_text(u.text)
                time.sleep(3)
                submit = driver.find_element(By.NAME, 'btnSend').click()
                wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/form/div/table')))
                all_df.append(crwal_table())
                time.sleep(5)
                driver.back()
                
final_df = pd.concat(all_df, ignore_index=True)
# print(final_df)
final_df.to_csv(f'{year}.csv',index=False)
driver.quit()