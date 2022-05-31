from lakeshore import Model336
from lakeshore.model_336 import Model336HeaterRange

# # connects to first available ls336 control. If no instrument is found specify port number



class local_intrument():
    def __init__(self):
        self.instrument = self.connect_ls336()
        self.heater_range = {
                            'OFF': Model336HeaterRange.OFF, 
                            'LO': Model336HeaterRange.LOW,
                            'MID': Model336HeaterRange.MEDIUM,
                            'HI': Model336HeaterRange.HIGH
                            }

### Properties

    @property
    def get_sample_temperature(self):
        """Returns temperature at sample position (channel A)

        Returns:
            float: temperature in Kelvin
        """
        return self.instrument.get_kelvin_reading("A")

    @property
    def get_tip_temperature(self):
        """Returns temperature at tip position (channel B)

        Returns:
            float: temperature in Kelvin
        """
        return self.instrument.get_kelvin_reading("B")

    @property
    def get_heater_power(self):
        """Returns the output percentage of heater 1 (in reference to the chosen output range)

        Returns:
            float: output percentage of full scale of current heater range of output channel
        """
        return self.instrument.get_heater_output(1)

    @property
    def get_setpoint(self):
        """Returns the setpoint of output 1

        Returns:
            float: setpoint value in kelvin (preferred units of output 1)
        """
        return self.instrument.get_control_setpoint(1)

    @property
    def get_heater_range(self):
        """Return current heater range setting of output 1

        Returns:
            Model336HeaterRange entry: heater range
        """
        return self.instrument.get_heater_range(1)

### Methods
    
    def connect_ls336(self):
        """conntects to first available ls336 intrument

        Returns:
            intrument class: a class representing the ls336 temperature controler
        """
        return Model336()

    def set_setpoint(self, setpoint):
        """Sets the temperature setpoint of heater output 1

        Args:
            setpoint (float): temperature setpoint in Kelvin

        Raises:
            CommunicationFailure: Is raised if temperature setpoint is not set correctly

        Returns:
            float: new temperature setpoint in Kelvin
        """
        self.instrument.set_control_setpoint(1, setpoint)
        setpoint_new = self.get_setpoint
        if setpoint_new != setpoint:
            raise CommunicationFailure("Setpoint was not set correctly!")
        return setpoint_new

    def set_heater_range(self,range):
        """sets the heater range to enabele or disable output

        Args:
            range (string): ('OFF', 'LO', 'MID', 'HI') key of dictonary self.heater_range

        Raises:
            CommunicationFailure: Is raised if heater range was not set corrtectly

        Returns:
            Model336HeaterRange entry: returns entry of IntEnum corresponding to set heater range
        """
        self.instrument.set_heater_range(1, self.heater_range[range])
        new_range = self.get_heater_range
        if new_range != self.heater_range[range]:
            raise CommunicationFailure("Heater was not set correctly")
        return new_range


class CommunicationFailure(Exception):
    pass






