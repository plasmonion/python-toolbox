# This module is defunct. VisaTransport should be used for serial communication instead, as it supports both serial and non-serial resources through the VISA interface. 
# The SerialTransport class is no longer necessary and has been removed to simplify the codebase and reduce maintenance overhead. 
# If you need to communicate with a serial instrument, please use VisaTransport with the appropriate resource name (e.g., "ASRL1::INSTR") 
# and configure the serial settings as needed.

import asyncio
import serial

from instrument_suite.core.transport import Transport


class SerialTransport(Transport):

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        timeout: float = 5.0,
        read_termination: str = "\n",
        write_termination: str = "\n",
    ):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.read_termination = read_termination
        self.write_termination = write_termination

        self.serial_port = None
        self.lock = asyncio.Lock()

    async def connect(self):
        self.serial_port = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
            write_timeout=self.timeout,
        )

    async def disconnect(self):
        if self.serial_port is not None:
            self.serial_port.close()
            self.serial_port = None

    async def write(self, command: str):
        if self.serial_port is None:
            raise RuntimeError("Serial transport is not connected")

        message = command + self.write_termination

        async with self.lock:
            self.serial_port.write(message.encode("ascii"))

    async def read(self) -> str:
        if self.serial_port is None:
            raise RuntimeError("Serial transport is not connected")

        async with self.lock:
            response = self.serial_port.readline()
            return response.decode("ascii").strip()

    async def query(self, command: str) -> str:
        if self.serial_port is None:
            raise RuntimeError("Serial transport is not connected")

        message = command + self.write_termination

        async with self.lock:
            self.serial_port.write(message.encode("ascii"))
            response = self.serial_port.readline()
            return response.decode("ascii").strip()