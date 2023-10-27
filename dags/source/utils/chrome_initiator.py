from selenium import webdriver
from selenium.webdriver.common.by import By

from source.interface.selenium_driver import SeleniumDriver


class Browser(SeleniumDriver) :

    def __init__(self, url) :
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(url)

    def single_element_by_css(self, class_name) :
        return self.driver.find_element(By.CSS_SELECTOR, class_name)

    def multiple_elements_by_css(self, class_name) :
        return self.driver.find_elements(By.CSS_SELECTOR, class_name)

    def single_element_by_class(self, class_name) :
        return self.driver.find_element(By.CLASS_NAME, class_name)

    def multiple_elements_by_class(self, class_name) :
        return self.driver.find_elements(By.CLASS_NAME, class_name)

    def single_element_by_tag(self, tag_name) :
        return self.driver.find_element(By.TAG_NAME, tag_name)

    def multiple_elements_by_tag(self, tag_name) :
        return self.driver.find_elements(By.TAG_NAME, tag_name)
