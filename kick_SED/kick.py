import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# define custom options for the Selenium driver
options = Options()
# free proxy server URL
proxy_server_url = "127.0.0.1:1080"
options.add_argument(f'--proxy-server={proxy_server_url}')

# create the ChromeDriver instance with custom options
browser = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()),
    # options=options
)
link = 'http://delotc.fsrar.ru/DELEC/CoreHost/auth/login?ReturnUrl=%2fDELEC%2f'
browser.get(link)

while True:
    try:
        input_logg = browser.find_element(By.XPATH,"(//input[@id='UserName'])[1]")
        input_logg.send_keys('SYSRP')

        input_pass = browser.find_element(By.XPATH,"(//input[@id='Password'])[1]")
        input_pass.send_keys('SYSRP')

        button_auth = browser.find_element(By.XPATH,"//button[contains(text(),'Войти')]")
        button_auth.click()
        time.sleep(1)

        while True:
            try:
                button_alert = browser.find_element(By.XPATH, "//div[@class='menu-logo']//a")
                button_alert.click()
                time.sleep(5)
            except:
                break

    except:
        button_kick = browser.find_element(By.XPATH, "//button[contains(text(),'Продолжить')]")
        button_kick.click()
        time.sleep(1)

        while True:
            try:
                button_alert = browser.find_element(By.XPATH, "//div[@class='menu-logo']//a")
                button_alert.click()
                time.sleep(5)
            except:
                break