import selenium
from selenium import webdriver
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


def find_data(inn,column_name, month):

    try:
        link = 'https://lk.fsrar.ru/account/loginform'
        browser = webdriver.Chrome()
        browser.get(link)

        input_loggin = browser.find_element(By.XPATH,"//input[@id='UserName']")
        input_loggin.send_keys('developer@fsrar.ru')
        input_password = browser.find_element(By.XPATH, "//input[@id='Password']")
        input_password.send_keys('developer')
        button_1 = browser.find_element(By.XPATH, " //input[@value='Войти']")
        button_1.click()
        time.sleep(0.1)

        second_link = 'https://lk.fsrar.ru/Goverment/ExciseDeclarations'
        browser.get(second_link)
        time.sleep(2)


        inn_input = browser.find_element(By.XPATH,"//input[@placeholder='ИНН']")
        inn_input.send_keys(inn)
        time.sleep(2)

        year_input = browser.find_element(By.XPATH, "//input[@placeholder='Год']")
        year_input.send_keys('2023')
        time.sleep(2)

        month_input = browser.find_element(By.XPATH, "//input[@placeholder='Месяц']")
        month_input.send_keys(month)
        time.sleep(2)

        all_rows = browser.find_elements(By.XPATH,"//table[@id='DeclarationsListTable']//tr[@role='row']")

        counter = 0
        for i in all_rows:
            try:
                actual = i.find_element(By.XPATH,"//tbody/tr[1]/td[8]").text
                if actual == 'Да':
                    button_next = i.find_element(By.XPATH,"//tr[@class='odd']//span[@class='fa fa-arrow-right']")
                    button_next.click()
                    time.sleep(2)
                    if column_name == 'declTaxBaseAnhydrousVolume':
                        button_next_1 = browser.find_element(By.XPATH, "//a[contains(text(),'Расчет сум. акц.')]")
                        button_next_1.click()
                        time.sleep(2)

                        button_next_2 = browser.find_element(By.XPATH, "//body[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[3]/table[1]/tbody[1]/tr[1]/td[4]/button[1]")
                        button_next_2.click()
                        time.sleep(2)

                        con_str = browser.find_element(By.CSS_SELECTOR,"body > div:nth-child(5) > div:nth-child(4) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(4) > div:nth-child(1) > div:nth-child(2) > div:nth-child(3) > table:nth-child(2) > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(1) > div:nth-child(3) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(3)").text[:-2]
                        con_str = con_str.replace(',','.')
                        counter += float(con_str)
                        return counter
            except selenium.common.exceptions.NoSuchElementException:
                return None





    finally:
        browser.quit()

inns = [9303019720,
        9402003103,
        3124010381,
        3128053185]

for inn in inns:
    print(f'INN {inn}\n________________________________')
    for month in range(1,13):
        from_lk = find_data(inn, "declTaxBaseAnhydrousVolume", month)
        print(f'Месяц {month} - {from_lk}')
    print('________________________________')