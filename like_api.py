from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import config

import asyncio
import time


def make_like(name, url, value):
    chrome_options = Options()
    chrome_options.add_argument(config.chrome_profile
                                )  # ("user-data-dir=C:\\Users\\kiril\\AppData\\Local\\Google\\Chrome Beta\\User Data\\Profile 1")
    chrome_options.binary_location = config.chrome_binary_exe_argument  # "C:\\Program Files\\Google\\Chrome Beta\\Application\\chrome.exe"
    driver = webdriver.Chrome(executable_path=config.chrome_driver_argument,
                              chrome_options=chrome_options)  # "C:\\Users\\kiril\\PycharmProjects\\tg_bot\\chromedriver.exe"

    def check_exists_by_xpath(xpath):
        try:
            driver.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return False
        return True
    try:
        driver.get('https://likest.ru/')
        time.sleep(2)
        if check_exists_by_xpath('''//*[@id="ulogin-button"]'''):
            id_box = driver.find_element(By.XPATH, '''//*[@id="ulogin-button"]''') #login vk
            id_box.click()
            time.sleep(3)
        driver.get('https://likest.ru/buy-likes')
        time.sleep(2)
        id_box = driver.find_element(By.XPATH, '''//*[@id="edit-title"]''')
        id_box.send_keys(name) #
        id_box = driver.find_element(By.XPATH, '''//*[@id="edit-link"]''')
        id_box.send_keys(url) #
        id_box = driver.find_element(By.XPATH, '''//*[@id="amount"]''')
        id_box.send_keys(value) #
        id_box = driver.find_element(By.XPATH, '''//*[@id="edit-submit"]''')
        id_box.click()
        time.sleep(1)
        # id_box = driver.find_element(By.XPATH, '''/html/body/div[3]/footer/div[1]/div/div/div/nav/ul/li[5]/a''') # exit
        # id_box.click()
    except Exception as ex:
        print(ex)
    finally:
        print()
        driver.close()
        driver.quit()

# make_like("test_task", "https://vk.com/wall201748903_2313", 10)


