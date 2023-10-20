from abc import abstractmethod


class SeleniumDriver :

    @abstractmethod
    def single_element_by_class(self, class_name) :
        pass

    @abstractmethod
    def multiple_elements_by_class(self, class_name) :
        pass

    @abstractmethod
    def single_element_by_tag(self, tag_name) :
        pass

    @abstractmethod
    def multiple_elements_by_tag(self, tag_name) :
        pass

    @abstractmethod
    def single_element_by_css(self, class_name) :
        pass

    @abstractmethod
    def multiple_elements_by_css(self, class_name) :
        pass
