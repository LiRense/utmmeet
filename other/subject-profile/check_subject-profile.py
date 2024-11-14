import time
from webbrowser import Chrome
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy.sql.functions import random
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import random
import all_info

# def some_magic(func):
#     item = getattr(a,i)
#     if callable(item):
#         item()

tokens = [
    'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiZGV2ZWxvcGVyIiwiZmlyc3ROYW1lIjoi0JjQstCw0L0g0JDQvdC00YDQtdC10LLQuNGHIiwibGFzdE5hbWUiOiLQnNCw0YDRgtC40YXQuNC9IiwibG9jYWxpdHkiOiLQky7QnNC-0YHQutCy0LAiLCJyZWdpb24iOiI1MCDQnNC-0YHQutC-0LLRgdC60LDRjyDQvtCx0LvQsNGB0YLRjCIsInJlZ2lvbkNvZGUiOiI1MCIsInVzZXJpZCI6IjQ1OSIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWVpZGVudGlmaWVyIjoiNDU5Iiwicm9sZWlkIjoiMTIiLCJwZXJtaXNzaW9ucyI6IlVzZXJzLFJvbGVzLE5ld3MsU3RhdGlzdGljYWxJbmYsUmV0YWlsLE1hcmtldFBhcnRpY2lwYW50cyxNYXJrZXRQYXJ0aWNpcGFudHNWMixSZXBvcnRzLE9yZ2FuaXphdGlvbnMsUmVwb3J0VGVtcGxhdGVzLFJldGFpbCxSZXRhaWwsUmV0YWlsLFJldGFpbCxSZXRhaWwsUmV0YWlsLFJldGFpbCxSZXRhaWwsUmV0YWlsLFJldGFpbCxSZXRhaWwsUmV0YWlsLFJldGFpbCxSZXRhaWwsUmV0YWlsLFJldGFpbCxSZXRhaWwsUmV0YWlsLFJldGFpbCxTdGF0aXN0aWNhbEluZixTdGF0aXN0aWNhbEluZixSZXRhaWwsUmV0YWlsLFJldGFpbCxSZXRhaWwsUmV0YWlsLFJldGFpbCxTdGF0aXN0aWNhbEluZixSZXRhaWwiLCJsaXN0UmVnaW9uQ29kZXMiOiI1MCIsImV4cCI6MTcyOTYyMzE3NywiaXNzIjoiQ0FFZ2FpcyIsImF1ZCI6IlVzZXJzIn0.uyATOqsD4sa_4bvfDAUd64vy-SIlJZTY1cS18gDjNho',
    '']

token = random.choice(tokens)
browser = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()),
    # options=options
)

link = 'https://lk-test.egais.ru/cabinet/general-info/country'
browser.get(link)
WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Войти с помощью ЭЦП']")))
browser.execute_script(f"window.localStorage.setItem('lk-test.egais.ru_lk-egais','{token}')")
browser.get(link)
time.sleep(0.5)
browser.get(link)
WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@class='mat-focus-indicator mat-button mat-button-base']")))
tabs = [all_info.random_param]

tab = random.choice(tabs)(WebDriverWait = WebDriverWait, EC = EC,  Select = Select, By = By, browser = browser)












