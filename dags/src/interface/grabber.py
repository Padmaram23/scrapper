from abc import abstractmethod


class Grab :

    @abstractmethod
    def execute_scraping(self) :
        pass

    @abstractmethod
    def __extract_data_from_page(self, url) :
        pass

    @abstractmethod
    def __store_extracted_data(self):
        pass
