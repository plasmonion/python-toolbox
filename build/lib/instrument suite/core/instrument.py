from abc import ABC, abstractmethod

class Instrument(ABC):

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def query(self, command):
        pass