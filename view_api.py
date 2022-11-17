from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import asyncio
from selenium.common.exceptions import NoSuchElementException
import config

import time


async def make_view(url, value):
    chrome_options = Options()
    chrome_options.add_argument(config.chrome_profile
        ) #("user-data-dir=C:\\Users\\kiril\\AppData\\Local\\Google\\Chrome Beta\\User Data\\Profile 1")
    chrome_options.binary_location = config.chrome_binary_exe_argument#"C:\\Program Files\\Google\\Chrome Beta\\Application\\chrome.exe"
    driver = webdriver.Chrome(executable_path= config.chrome_driver_argument,
                              chrome_options=chrome_options) #"C:\\Users\\kiril\\PycharmProjects\\tg_bot\\chromedriver.exe"

    def check_exists_by_xpath(xpath):
        try:
            driver.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return False
        return True
    try:
        driver.get('https://lk.vkviews.ru/')
        #time.sleep(30)
        if check_exists_by_xpath('''/html/body/div[1]/div/div/div[2]/button[1]'''):
            id_box = driver.find_element(By.XPATH, '''/html/body/div[1]/div/div/div[2]/button[1]''')  # login vk
            id_box.click()
            time.sleep(1)

        driver.get('https://lk.vkviews.ru/task/add/post')
        #time.sleep(1)
        if check_exists_by_xpath('''/html/body/div[1]/div/div/div/div[2]/form/div[2]/div/div[2]/input'''):
            id_box = driver.find_element(By.XPATH,
                                         '''/html/body/div[1]/div/div/div/div[2]/form/div[2]/div/div[2]/input''')
            id_box.send_keys(url)  #
            id_box = driver.find_element(By.XPATH,
                                         '''/html/body/div[1]/div/div/div/div[2]/form/div[4]/div[2]/div[1]/input''')
            id_box.clear()
            id_box.send_keys(value)  #
            if check_exists_by_xpath('''/html/body/div[1]/div/div/div/div[2]/form/div[9]/button'''):
                id_box = driver.find_element(By.XPATH,
                                             '''/html/body/div[1]/div/div/div/div[2]/form/div[9]/button''')  # make order
            elif check_exists_by_xpath('''/html/body/div[1]/div/div/div/div[2]/form/div[10]/button'''):
                id_box = driver.find_element(By.XPATH,
                                             '''/html/body/div[1]/div/div/div/div[2]/form/div[10]/button''')  # make order
            else:
                id_box = driver.find_element(By.XPATH,
                                             '''/html/body/div[1]/div/div/div/div[2]/form/div[8]/button''')  # make order
            id_box.click()
        else:
            id_box = driver.find_element(By.XPATH,
                                         '''/html/body/div[1]/div/div/div/div[3]/form/div[2]/div/div[2]/input''')
            id_box.send_keys(url)  #
            id_box = driver.find_element(By.XPATH,
                                         '''/html/body/div[1]/div/div/div/div[3]/form/div[4]/div[2]/div[1]/input''')
            id_box.clear()
            id_box.send_keys(value)  #
            if check_exists_by_xpath('''/html/body/div[1]/div/div/div/div[3]/form/div[9]/button'''):
                id_box = driver.find_element(By.XPATH,
                                             '''/html/body/div[1]/div/div/div/div[3]/form/div[9]/button''')  # make order
            elif check_exists_by_xpath('''/html/body/div[1]/div/div/div/div[3]/form/div[10]/button'''):
                id_box = driver.find_element(By.XPATH,
                                             '''/html/body/div[1]/div/div/div/div[3]/form/div[10]/button''')  # make order
            else:
                id_box = driver.find_element(By.XPATH,
                                             '''/html/body/div[1]/div/div/div/div[3]/form/div[8]/button''')  # make order
            id_box.click()


        # решение капчи:
        time.sleep(2)

        for tr in range(0, 5):
            if check_exists_by_xpath('''/html/body/div[4]/div[2]/div/div[2]/div/div[2]/div[2]'''):
                id_box = driver.find_element(By.XPATH,
                                             '''/html/body/div[4]/div[2]/div/div[2]/div/div[2]/div[2]''')  # 2captcha расширение
                id_box.click()
                break
            else:
                if check_exists_by_xpath('''/html/body/div[4]/div[2]/div/h3'''):  # чек на конец
                    break
                time.sleep(2)
        for tr in range(0, 24):
            time.sleep(5)  # /html/body/div[4]/div[3]/div/h3
            if check_exists_by_xpath('''/html/body/div[4]/div[2]/div/h3'''):  # чек на конец
                break
        # time.sleep(1)
        # id_box = driver.find_element(By.XPATH, '''/html/body/div[4]/div[2]/div/div[1]''')  # close order
        # id_box.click()
        # id_box = driver.find_element(By.XPATH, '''/html/body/div[1]/header/div/div[2]/div[2]/div/img''') # выход
        # id_box.click()
        # time.sleep(1)
        # id_box = driver.find_element(By.XPATH, '''/html/body/div[1]/header/div/div[2]/div[2]/ul/li[3]/a''') # exit
        # id_box.click()
        # time.sleep(1)
    except Exception as ex:
        print(ex)
    finally:
        driver.quit()

#make_view("https://vk.com/wall436857739_139", 1)