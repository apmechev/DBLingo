from abc import ABC, abstractmethod

class AbstractSink(ABC):
    @abstractmethod
    def append(self, data):
        pass

    @abstractmethod
    def get_last_timestamp(self):
        pass
