try:
    from lakeshore import LS224
except ImportError as e:
    raise ImportError(
        "The lakeshore package is required to use the LS224 driver. "
        "Install it with:\n"
        "pip install lakeshore"
        "or navigate to the root directory and run:\n"
        "pip install ."
        "to install the entire toolbox."
    ) from e

from instrument_suite.core.instrument import Instrument

from math import nan

class LS224(Instrument):
    """
    Driver for the Lakeshore 224 temperature controller.

    The class does not care whether communication is GPIB, serial, USB, or TCP/IP.
    It only requires a transport object with connect, disconnect, write, and query methods.
    """

    VALID_CHANNELS = {
        "A", "B",
        "C1", "C2", "C3", "C4", "C5",
        "D1", "D2", "D3", "D4", "D5",
    }

    def __init__(self, transport, name="LS224"): 
        self.transport = transport # We abstract the transport layer so that the driver can work with any communication method (GPIB, serial, USB, TCP/IP).
        self.name = name # The name attribute is optional and can be used for logging or identification purposes. Default is "LS224".

# The connect method establishes a connection to the instrument using the transport's connect method.
    async def connect(self):
        await self.transport.connect() 

# The disconnect method closes the connection to the instrument using the transport's disconnect method.
    async def disconnect(self):
        await self.transport.disconnect()

# The write method sends a command to the instrument using the transport's write method.
    async def write(self, command: str):
        await self.transport.write(command)

# The query method sends a command to the instrument and waits for a response using the transport's query method.
    async def query(self, command: str) -> str:
        return await self.transport.query(command)

# The _validate_channel method checks if the provided channel is valid and returns it in uppercase. If the channel is invalid, it raises a ValueError.    
    def _validate_channel(self, channel: str):
        channel = channel.upper()

        if channel not in self.VALID_CHANNELS:
            raise ValueError(f"Invalid LS224 channel: '{channel}'.")
        
        return channel

# The get_kelvin_reading method retrieves the temperature reading in Kelvin for the specified channel. 
# It validates the channel, sends the appropriate command to the instrument, and returns the response as a float.
    async def get_kelvin_reading(self, channel: str) -> float:
        channel = self._validate_channel(channel)

        response = await self.query(f"KRDG? {channel}")
        
        # We attempt to convert the response to a float.
        try:
            return float(response)
        
        # If the response cannot be converted to a float, we raise a ValueError with a descriptive message.
        except ValueError as e:
            raise ValueError(
                f"{self.name} returned a non-numeric temperature "
                f"for channel '{channel}': '{response!r}'."
             ) from e

# The get_resistance_reading method retrieves the resistance reading for the specified channel. 
# It validates the channel, sends the appropriate command to the instrument, and returns the response as a float.
    async def get_resistance_reading(self, channel: str) -> float:
        channel = self._validate_channel(channel)

        response = await self.query(f"SRDG? {channel}")

        # We attempt to convert the response to a float.
        try:
            return float(response)
        
        # If the response cannot be converted to a float, we raise a ValueError with a descriptive message.
        except ValueError as e:
            raise ValueError(
                f"{self.name} returned a non-numeric resistance "
                f"for channel '{channel}': '{response!r}'."
             ) from e


    async def get_kelvin_readings(
            self,
            channels: list[str]
    ) -> dict[str, float]:
        """
        Retrieves the temperature readings in Kelvin for the specified channels.
        """

        command = ",".join(
            f"KRDG? {channel}"
            for channel in channels
        )

        response = await self.query(command)

        values = response.split(",")
     
        readings = {}

        for value, channel in zip(values, channels):
            try:
                readings[channel] = float(value)
            except ValueError as e:
            # If we encounter an error while reading a channel, we log the error and continue with the next channel.
                print(
                    f"Error reading channel '{channel}': {e}"
                )
                readings[channel] = nan
        
        return readings


  