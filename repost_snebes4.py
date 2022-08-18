from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import config

import asyncio
import time


def make_repost(url, value):
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
        driver.get('https://snebes.ru/index.php')
        time.sleep(2)
        if check_exists_by_xpath('''/html/body/div[2]/div/div/div[1]/center/center[1]/div/div/div'''):
            id_box = driver.find_element(By.XPATH, '''/html/body/div[2]/div/div/div[1]/center/center[1]/div/div/div''') #login vk
            id_box.click()
            time.sleep(3)
        driver.get('https://snebes.ru/add_tasks.php?t=4')
        time.sleep(1)
        id_box = driver.find_element(By.XPATH, '''//*[@id="url"]''') #
        id_box.send_keys(url) #
        id_box = driver.find_element(By.XPATH, '''//*[@id="pri"]''') # цена баллов
        id_box.clear()
        id_box.send_keys("150")
        id_box = driver.find_element(By.XPATH, '''//*[@id="ko"]''') # кол-во
        id_box.clear()
        id_box.send_keys(value) #
        id_box = driver.find_element(By.XPATH, '''//*[@id="button1"]''')
        id_box.click()
        time.sleep(3)
    except Exception as ex:
        print(ex)
    finally:
        driver.quit()

# make_like("https://vk.com/wall-137221094_16", 10)


