from abc import ABC, abstractmethod


class Downloadable(ABC):
    @abstractmethod

    def download(self):
        raise NotImplementedError("Downloadable.download() is not implemented")