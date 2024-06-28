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
        browser.implicitly_wait(5)

        second_link = 'https://lk.fsrar.ru/Goverment/ExciseDeclarations'
        browser.get(second_link)
        browser.implicitly_wait(5)


        inn_input = browser.find_element(By.XPATH,"//input[@placeholder='ИНН']")
        inn_input.send_keys(inn)
        browser.implicitly_wait(2)
        try:
            no_element = browser.find_element(By.XPATH,"//td[@class='dataTables_empty']")
            return 'No element'
        except selenium.common.exceptions.NoSuchElementException:
            pass
        year_input = browser.find_element(By.XPATH, "//input[@placeholder='Год']")
        year_input.send_keys('2023')
        browser.implicitly_wait(2)
        try:
            no_element = browser.find_element(By.XPATH,"//td[@class='dataTables_empty']")
            return 'No element'
        except selenium.common.exceptions.NoSuchElementException:
            pass

        month_input = browser.find_element(By.XPATH, "//input[@placeholder='Месяц']")
        month_input.send_keys(month)
        browser.implicitly_wait(2)
        try:
            no_element = browser.find_element(By.XPATH,"//td[@class='dataTables_empty']")
            return None
        except selenium.common.exceptions.NoSuchElementException:
            pass

        browser.implicitly_wait(5)
        act = browser.find_element(By.CSS_SELECTOR,"th[aria-label='Актуальность: activate to sort column ascending']")
        act.click()
        time.sleep(2)
        act.click()
        time.sleep(2)

        all_rows = browser.find_elements(By.XPATH,"//table[@id='DeclarationsListTable']//tr[@role='row']")

        counter = 0
        for i in all_rows:
            try:
                actual = i.find_element(By.XPATH,"//tbody/tr[1]/td[8]").text
                if actual == 'Да':
                    button_next = i.find_element(By.XPATH,"//tr[@class='odd']//span[@class='fa fa-arrow-right']")
                    button_next.click()
                    browser.implicitly_wait(5)
                    if column_name == 'declTaxBaseAnhydrousVolume':
                        button_next_1 = browser.find_element(By.XPATH, "//a[contains(text(),'Расчет сум. акц.')]")
                        button_next_1.click()
                        browser.implicitly_wait(10)

                        codes_vid = browser.find_elements(By.XPATH,'//div[@id="tab2"]//table[@class="table table-bordered dataTable excise_declar_app"]/tbody/tr[not(@class="declaration-item")]')
                        for id, j in enumerate(codes_vid):
                            code_vid = j.find_element(By.CSS_SELECTOR, "td:nth-child(1)")
                            if int(code_vid.text) in [231, 224, 225, 226, 227, 290]:
                                button_next_2 = j.find_element(By.CSS_SELECTOR,"td:nth-child(4) button:nth-child(1) span:nth-child(1)")
                                button_next_2.click()
                                browser.implicitly_wait(5)

                                con_str = browser.find_element(By.XPATH,f'(//div[@id="tab2"]//table[@class="table table-bordered dataTable excise_declar_app"]/tbody/tr[not(@class="declaration-item")])[{id+1}]/following::tr[1]//td/span[@data-toggle="tooltip"][normalize-space()="10001"]/following::td[2]').text
                                con_str = con_str.replace(',', '.')
                                counter += float(con_str)
                        return counter

                        # code_vid_poakciz = browser.find_element(By.XPATH,"(//td[contains(text(),'225')])[1]")


                    elif column_name == 'declTaxBaseVolume':
                        button_next_1 = browser.find_element(By.XPATH, "//a[contains(text(),'Расчет сум. акц.')]")
                        button_next_1.click()
                        time.sleep(5)

                        codes_vid = browser.find_elements(By.XPATH,
                                                          '//div[@id="tab2"]//table[@class="table table-bordered dataTable excise_declar_app"]/tbody/tr[not(@class="declaration-item")]')
                        for id, j in enumerate(codes_vid):
                            code_vid = j.find_element(By.CSS_SELECTOR, "td:nth-child(1)").text
                            # print(code_vid)
                            if int(code_vid) in [232, 251, 252, 253, 254, 274, 275, 276, 277, 287, 288, 297, 310, 320, 330 ]:
                                button_next_2 = j.find_element(By.XPATH,
                                                                     "//body[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[3]/table[1]/tbody[1]/tr[1]/td[4]/button[1]")
                                button_next_2.click()
                                browser.implicitly_wait(5)

                                con_str = browser.find_element(By.CSS_SELECTOR,"body > div:nth-child(5) > div:nth-child(4) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(4) > div:nth-child(1) > div:nth-child(2) > div:nth-child(3) > table:nth-child(2) > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(1) > div:nth-child(3) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(3)").text
                                con_str = con_str.replace(',', '.')
                                counter += float(con_str)
                                return counter
                    elif column_name == 'declSumForTaxDeductGrape':
                        try:
                            button_next_1 = browser.find_element(By.XPATH, "//a[contains(text(),'Сумма акциза на виноград')]")
                            button_next_1.click()
                            browser.implicitly_wait(5)

                            all_grapes = browser.find_elements(By.XPATH, "//div[@id='tab_vino']/table/tbody/tr[not(@class='declaration-item')]")
                            for id, j in enumerate(all_grapes):
                                one_grape = j.find_element(By.CSS_SELECTOR,"td:nth-child(1)").text
                                if int(one_grape) in [10024, 10025, 10026]:
                                    button_next_1 = j.find_element(By.CSS_SELECTOR,"td:nth-child(5) button:nth-child(1) span:nth-child(1)")
                                    button_next_1.click()
                                    time.sleep(1)
                                    summa_akciz = browser.find_element(By.XPATH, f"(//td[contains(text(),'Сумма акциза, подлежащая налоговому вычету')])[{id+1}]/following::td[1]").text
                                    counter += int(summa_akciz.replace(' ',''))
                                browser.implicitly_wait(5)
                            return counter
                        except:
                            return None

                    elif column_name == 'declSumTaxDeductNonGrape':
                        try:
                            button_next_1 = browser.find_element(By.XPATH, "//a[contains(text(),'Расчет сум. акц.')]")
                            button_next_1.click()
                            browser.implicitly_wait(5)

                            codes_vid = browser.find_elements(By.XPATH,'//div[@id="tab2"]//table[@class="table table-bordered dataTable excise_declar_app"]/tbody/tr[not(@class="declaration-item")]')
                            for id, j in enumerate(codes_vid):

                                button_next_2 = j.find_element(By.CSS_SELECTOR,"td:nth-child(4) button:nth-child(1) span:nth-child(1)")
                                button_next_2.click()
                                browser.implicitly_wait(5)

                                con_str = browser.find_elements(By.XPATH,f"(//h4[contains(text(),'2.3. Сумма акциза (авансового платежа акциза), подлежащая налоговому вычету')])[{id+1}]/following::table[1]/tbody/tr")
                                for id2, k in enumerate(con_str):
                                    try:
                                        i_finder = k.find_element(By.XPATH,f"(//h4[contains(text(),'2.3. Сумма акциза (авансового платежа акциза), подлежащая налоговому вычету')])[{id+1}]/following::table[1]/tbody/tr/td/i[contains(text(),'Нет данных')]")
                                        continue
                                    except:
                                        code_checker = k.find_element(By.CSS_SELECTOR,"td:nth-child(1)").text
                                        if int(code_checker) not in [30014, 30015, 30016]:
                                            new_str = k.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text
                                            # print(id+1,id2+1, code_checker,new_str)
                                            new_str = new_str.replace(',', '.')
                                            new_str = new_str.replace(' ', '')
                                            counter += float(new_str)
                                        browser.implicitly_wait(5) #(//h4[contains(text(),'2.3. Сумма акциза (авансового платежа акциза), под')])[4]/following::table[1]/tbody/tr//span[@class='init-tooltip']/following::td[2]
                            return counter
                        except:
                            return None

            except selenium.common.exceptions.NoSuchElementException:
                return find_data(inn,column_name, month)
    except selenium.common.exceptions.ElementClickInterceptedException:
        return find_data(inn,column_name, month)
    except selenium.common.exceptions.NoSuchElementException:
        return find_data(inn, column_name, month)

    finally:
        browser.quit()

columns = ['declTaxBaseVolume',
           'declTaxBaseAnhydrousVolume',
           'declSumForTaxDeductGrape',
           'declSumTaxDeductNonGrape',
           'declSumOnGrape']

with open('inn.txt','r') as innns:
    inns = innns.readlines()

file_old_lk = open('old_lk2','w')

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
