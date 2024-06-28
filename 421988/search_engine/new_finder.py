import selenium
from selenium import webdriver
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait


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
        time.sleep(1.5)

        second_link = 'https://lk.fsrar.ru/Goverment/ExciseDeclarations'
        browser.get(second_link)
        time.sleep(1.5)

        start = 0
        while start != 1:
            try:
                inn_input = browser.find_element(By.XPATH,"//input[@placeholder='ИНН']")
                inn_input.send_keys(inn)
                try:
                    no_element = browser.find_element(By.XPATH, "//td[@class='dataTables_empty']")
                    if no_element.text == 'Не найдено ни одного элемента.':
                        return None
                except selenium.common.exceptions.NoSuchElementException:
                    pass
                end = 1
            except:
                time.sleep(1)
                end = 0
                pass
            finally:
                if end != 0:
                    start = 1

        start = 0
        while start != 1:
            try:
                year_input = browser.find_element(By.XPATH, "//input[@placeholder='Год']")
                year_input.send_keys('2023')
                try:
                    no_element = browser.find_element(By.XPATH, "//td[@class='dataTables_empty']")
                    if no_element.text == 'Не найдено ни одного элемента.':
                        return None
                except selenium.common.exceptions.NoSuchElementException:
                    pass
                end = 1
            except:
                time.sleep(1)
                end = 0
                pass
            finally:
                if end != 0:
                    start = 1



        start = 0
        while start != 1:
            try:
                month_input = browser.find_element(By.XPATH, "//input[@placeholder='Месяц']")
                month_input.send_keys(month)
                try:
                    no_element = browser.find_element(By.XPATH, "//td[@class='dataTables_empty']")
                    if no_element.text == 'Не найдено ни одного элемента.':
                        return None
                except selenium.common.exceptions.NoSuchElementException:
                    pass
                end = 1
            except:
                time.sleep(1)
                end = 0
                pass
            finally:
                if end != 0:
                    start = 1
        time.sleep(2)

        start = 0
        while start != 1:
            try:
                act = browser.find_element(By.CSS_SELECTOR,
                                           "th[aria-label='Актуальность: activate to sort column ascending']")
                act.click()
                time.sleep(1)
                act.click()
                time.sleep(1)
                try:
                    no_element = browser.find_element(By.XPATH, "//td[@class='dataTables_empty']")
                    if no_element.text == 'Не найдено ни одного элемента.':
                        return None
                except selenium.common.exceptions.NoSuchElementException:
                    pass
                end = 1
            except:
                time.sleep(1)
                end = 0
                pass
            finally:
                if end != 0:
                    start = 1



        start = 0
        while start != 1:
            try:
                all_rows = browser.find_elements(By.XPATH, "//table[@id='DeclarationsListTable']//tr[@role='row']")
                try:
                    no_element = browser.find_element(By.XPATH,"//td[@class='dataTables_empty']")
                    if no_element.text == 'Не найдено ни одного элемента.':
                        return None
                except selenium.common.exceptions.NoSuchElementException:
                    pass
                end = 1
            except:
                time.sleep(1)
                end = 0
                pass
            finally:
                if end != 0:
                    start = 1
                    counter = 0

        for i in all_rows:

            actual = i.find_element(By.XPATH,"//tbody/tr[1]/td[8]").text
            if actual == 'Да':
                start = 0
                while start != 1:
                    try:
                        button_next = i.find_element(By.XPATH, "//tr[@class='odd']//span[@class='fa fa-arrow-right']")
                        button_next.click()
                        end = 1
                    except:
                        time.sleep(1)
                        end = 0
                        pass
                    finally:
                        if end != 0:
                            start = 1


                if column_name == 'declTaxBaseVolume':
                    start = 0
                    while start != 1:
                        try:
                            button_next_1 = browser.find_element(By.XPATH, "//a[contains(text(),'Расчет сум. акц.')]")
                            button_next_1.click()
                            end = 1
                        except:
                            time.sleep(1)
                            end = 0
                            pass
                        finally:
                            if end != 0:
                                start = 1

                    start = 0
                    while start != 1:
                        try:
                            codes_vid = browser.find_elements(By.XPATH,
                                                              '//div[@id="tab2"]//table[@class="table table-bordered dataTable excise_declar_app"]/tbody/tr[not(@class="declaration-item")]')
                            time.sleep(2)
                            for id, j in enumerate(codes_vid):
                                code_vid = j.find_element(By.CSS_SELECTOR, "td:nth-child(1)").text
                                # print(code_vid)
                                if int(code_vid) in [232, 251, 252, 253, 254, 274, 275, 276, 277, 287, 288, 297, 310,
                                                     320, 330]:

                                    button_next_2 = j.find_element(By.XPATH,
                                                                   "//body[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[3]/table[1]/tbody[1]/tr[1]/td[4]/button[1]")
                                    button_next_2.click()
                                    time.sleep(5)

                                    con_str = browser.find_element(By.CSS_SELECTOR,
                                                                   "body > div:nth-child(5) > div:nth-child(4) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(4) > div:nth-child(1) > div:nth-child(2) > div:nth-child(3) > table:nth-child(2) > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(1) > div:nth-child(3) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(3)").text
                                    con_str = con_str.replace(',', '.')
                                    counter += float(con_str)
                                    end = 1
                                else:
                                    return None

                            return counter
                        except:
                            time.sleep(1)
                            end = 0
                            pass
                        finally:
                            if end != 0:
                                start = 1


    finally:
        browser.quit()

columns = ['declTaxBaseVolume',
           'declTaxBaseAnhydrousVolume',
           'declSumForTaxDeductGrape',
           'declSumTaxDeductNonGrape',
           'declSumOnGrape']

with open('inn.txt','r') as innns:
    inns = innns.readlines()

file_old_lk = open('old_lk3','w')

for inn in inns:
    file_old_lk.write(f'INN {int(inn)}\n________________________________\n')
    print(f'INN {inn}________________________________')
    for month in range(1,13):
        from_lk = find_data(inn, "declTaxBaseVolume", month)
        if from_lk == 'No element':
            for month1 in range(1,13):
                file_old_lk.write(f'Месяц {month1} - None\n')
                print(f'Месяц {month1} - None')
            break
        file_old_lk.write(f'Месяц {month} - {from_lk}\n')
        print(f'Месяц {month} - {from_lk}')
    file_old_lk.write('________________________________\n')
    print('________________________________')
