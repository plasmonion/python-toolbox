import asyncio
import pyvisa

from instrument_suite.core.transport import Transport

class VisaTransport(Transport):
    """
    A transport class that uses PyVISA to communicate with instruments over GPIB, serial, USB, or TCP/IP.

    This class abstracts the communication layer and provides a consistent interface for sending commands and receiving responses.
    """

    def __init__(
        self, 
        resource_name: str,
        timeout_ms: int = 5000,
        read_termination: str = "\n",
        write_termination: str = "\n",
    ):
        self.resource_name = resource_name
        self.timeout_ms = timeout_ms
        self.read_termination = read_termination
        self.write_termination = write_termination

        self.resource_manager = None
        self.instrument = None
        self.lock = asyncio.Lock() # We use an asyncio lock to ensure that only one operation (connect, disconnect, write, query) can be performed at a time, preventing race conditions
    

    async def connect(self):
        self.resource_manager = pyvisa.ResourceManager()
        self.instrument = self.resource_manager.open_resource(self.resource_name)
        self.instrument.timeout = self.timeout_ms
        self.instrument.read_termination = self.read_termination
        self.instrument.write_termination = self.write_termination


    async def disconnect(self):
        if self.instrument is not None:
            self.instrument.close()
            self.instrument = None

        if self.resource_manager is not None:
            self.resource_manager.close()
            self.resource_manager = None

            
    async def write(self, command: str):
        if self.instrument is None:
            raise RuntimeError("VisaTransport is not connected.")
        
        async with self.lock: # We acquire the lock to ensure that this write operation is not interrupted by another operation.
            self.instrument.write(command)


    async def query(self, command: str) -> str:
        if self.instrument is None:
            raise RuntimeError("VisaTransport is not connected.")
        
        async with self.lock: # We acquire the lock to ensure that this query operation is not interrupted by another operation.
            return self.instrument.query(command).strip()
        