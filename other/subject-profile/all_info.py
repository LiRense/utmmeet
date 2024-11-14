import random
import time


def ai_regions(WebDriverWait, EC, Select, By, browser):
    link = 'https://lk-test.egais.ru/cabinet/general-info/country'
    browser.get(link)
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "44")))
    region = browser.find_element(By.ID, "mat-select-value-1")
    region.click()
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Южный федеральный округ']")))
    region = browser.find_element(By.XPATH, "//*[text()='Южный федеральный округ']")
    region.click()
    time.sleep(10000)

def ai_stat_relize(Select, By, browser):
    link = 'https://lk-test.egais.ru/cabinet/general-info'
    browser.get(link)

    stat = Select(browser.find_element(By.XPATH, "(//div[@class='mat-form-field-infix ng-tns-c58-284'])[1]"))
    stat.send_keys('Недружественные страны')

def ai_stat_person(Select, By, browser):
    link = 'https://lk-test.egais.ru/cabinet/general-info'
    browser.get(link)

    stat = browser.find_element(By.XPATH, "(//div[@class='mat-form-field-infix ng-tns-c58-284'])[1]")
    stat.send_keys('Старше 18 лет')

def random_param(**kwargs):
    functions = [ai_regions
                 ]
    return random.choice(functions)(**kwargs)