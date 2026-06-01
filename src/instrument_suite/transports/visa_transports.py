import asyncio
import pyvisa
from pyvisa.constants import (Parity, StopBits, FlowControl)

from instrument_suite.core.transport import Transport

class VisaTransport(Transport):
    """
    A transport class that uses PyVISA to communicate with instruments over GPIB, USB, serial, or TCP/IP.

    This class abstracts the communication layer and provides a consistent interface for sending commands and receiving responses.
    """

    def __init__(
        self, 
        resource_name: str,
        timeout_ms: int = 5000,
        read_termination: str = "\n",
        write_termination: str = "\n",
        baud_rate: int | None = None, # The baud_rate parameter is only relevant for serial resources (ASRL). If the resource is not a serial resource, this parameter will be ignored.
        data_bits: int | None = None, # The data_bits parameter is only relevant for serial resources (ASRL). If the resource is not a serial resource, this parameter will be ignored.
        parity: Parity | None = None, # The parity parameter is only relevant for serial resources (ASRL). If the resource is not a serial resource, this parameter will be ignored.
        stop_bits: StopBits | None = None, # The stop_bits parameter is only relevant for serial resources (ASRL). If the resource is not a serial resource, this parameter will be ignored.
        flow_control: FlowControl | None = None, # The flow_control parameter is only relevant for serial resources (ASRL). If the resource is not a serial resource, this parameter will be ignored.
    ):
        self.resource_name = resource_name
        self.timeout_ms = timeout_ms
        self.read_termination = read_termination
        self.write_termination = write_termination

        self.baud_rate = baud_rate # The baud rate for serial communication. This is only applicable if the resource is a serial resource (ASRL).
        self.data_bits = data_bits # The number of data bits for serial communication. This is only applicable if the resource is a serial resource (ASRL).
        self.parity = parity # The parity setting for serial communication. This is only applicable if the resource is a serial resource (ASRL).
        self.stop_bits = stop_bits # The number of stop bits for serial communication. This is only applicable if the resource is a serial resource (ASRL).
        self.flow_control = flow_control # The flow control setting for serial communication. This is only applicable if the resource is a serial resource (ASRL).

        self.resource_manager = None 
        self.instrument = None
        self.lock = asyncio.Lock() # We use an asyncio lock to ensure that only one operation (connect, disconnect, write, query) can be performed at a time, preventing race conditions
    
    @property
    def is_serial_resource(self) -> bool:
        return self.resource_name.upper().startswith("ASRL")

    async def connect(self):
        self.resource_manager = pyvisa.ResourceManager()
        self.instrument = self.resource_manager.open_resource(self.resource_name)
        self.instrument.timeout = self.timeout_ms
        self.instrument.read_termination = self.read_termination
        self.instrument.write_termination = self.write_termination

        # Serial-specific VISA settings
        if self.baud_rate is not None:
            self.session.baud_rate = self.baud_rate

        if self.data_bits is not None:
            self.session.data_bits = self.data_bits

        if self.parity is not None:
            self.session.parity = self.parity

        if self.stop_bits is not None:
            self.session.stop_bits = self.stop_bits

        if self.flow_control is not None:
            self.session.flow_control = self.flow_control


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
        