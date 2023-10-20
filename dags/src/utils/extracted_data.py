from selenium.webdriver.common.by import By

from src.interface.data_from_driver import DataFromDriver


class RawData(DataFromDriver):
    def single_element_by_css(self, data, class_name) :
        return data.find_element(By.CSS_SELECTOR, class_name)

    def multiple_elements_by_css(self, data, class_name) :
        return data.find_elements(By.CSS_SELECTOR, class_name)

    def single_element_by_class(self, data, class_name) :
        return data.find_element(By.CLASS_NAME, class_name)

    def multiple_elements_by_class(self, data, class_name) :
        return data.find_elements(By.CLASS_NAME, class_name)

    def single_element_by_tag(self, data, tag_name) :
        return data.find_element(By.TAG_NAME, tag_name)

    def multiple_elements_by_tag(self, data, tag_name) :
        return data.find_elements(By.TAG_NAME, tag_name)
