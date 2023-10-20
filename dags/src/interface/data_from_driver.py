from abc import abstractmethod


class DataFromDriver :

    @abstractmethod
    def single_element_by_class(self, data, class_name) :
        pass

    @abstractmethod
    def multiple_elements_by_class(self, data, class_name) :
        pass

    @abstractmethod
    def single_element_by_tag(self, data, tag_name) :
        pass

    @abstractmethod
    def multiple_elements_by_tag(self, data, tag_name) :
        pass

    @abstractmethod
    def single_element_by_css(self, data, class_name) :
        pass

    @abstractmethod
    def multiple_elements_by_css(self, data, class_name) :
        pass
