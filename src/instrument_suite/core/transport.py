from abc import ABC, abstractmethod

class Transport(ABC):

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def write(self, command: str):
        pass

    @abstractmethod
    async def read(self) -> str:
        pass

    @abstractmethod
    async def query(self, command: str) -> str:
        await self.write(command)
        return await self.read()