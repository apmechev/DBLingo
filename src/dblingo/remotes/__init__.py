from abc import ABC, abstractmethod

class AbstractRemote(ABC):
    @abstractmethod
    def upload(self, file_path):
        pass
