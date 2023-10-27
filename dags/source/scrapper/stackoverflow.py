from source.constants.endpoint_urls import Endpoints
from source.enum.time_period import Duration
from source.interface.grabber import Grab
from source.utils import helper_function
from source.utils.chrome_initiator import Browser
from source.utils.extracted_data import RawData
from source.storage.influx_db import InfluxDB


class ScrapingDataFromStackOverFlow(Grab):

    def __init__(self):

        # scraped data will be stored in this array
        self.data_list = []

    def execute_scraping(self):
        # can write your own function depending upon your website
        # In the parameter can specify the number of pages you want to scrap form the website
        self.__stack_scraping(5)

    def __extract_data_from_page(self, url):
        try:
            browser = Browser(url)
            raw_data = RawData()
            for data in browser.multiple_elements_by_class("grid--item"):
                tag_name = raw_data.single_element_by_class(
                    data, "post-tag").text
                days = raw_data.single_element_by_class(data, 'fc-black-400')
                no_of_questions = helper_function.separate_number(
                    raw_data.single_element_by_tag(days, 'div').text)

                rate_of_questions = raw_data.single_element_by_css(
                    data, ".s-anchors.s-anchors__inherit")
                time_scope_of_question = raw_data.multiple_elements_by_tag(
                    rate_of_questions, 'a')

                today, week, month, year = None, None, None, None

                for rate in time_scope_of_question:
                    time_frame = rate.text.upper()
                    count = helper_function.separate_number(time_frame)
                    if Duration.TODAY.name in time_frame:
                        today = count
                    elif Duration.WEEK.name in time_frame:
                        week = count

                self.data_list.append({
                    "measurement": tag_name,
                    "fields": {
                        "no_of_questions": no_of_questions,
                        "today": today,
                        "week": week,
                    }
                })

        except Exception as e:
            print("The error is in storing data: ", e)

        finally:
            browser.driver.quit()

    def __stack_scraping(self, num_pages):
        try:
            main_url = Endpoints.STACK_OVERFLOW_URL

            # Loop through pages and extract data
            for page_num in range(1, num_pages + 1):
                new_url = main_url.replace('page=1', f'page={page_num}')
                self.__extract_data_from_page(new_url)

            self.__store_extracted_data()

            for data in self.data_list:
                print(data)

        except Exception as e:
            print("The error is : ", e)

    # storing extracted data in a database:
    def __store_extracted_data(self):
        influx = InfluxDB()
        influx.storage('stack_overflow', self.data_list)