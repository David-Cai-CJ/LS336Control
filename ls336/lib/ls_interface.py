from time import sleep
from lakeshore import Model336
from lakeshore.model_336 import Model336HeaterRange

# # connects to first available ls336 control. If no instrument is found specify port number

class local_intrument():
    def __init__(self, heater_channel):
        self.instrument = self.connect_ls336()
        self.heater_range = {
                            'OFF': Model336HeaterRange.OFF,
                            'LO': Model336HeaterRange.LOW,
                            'MID': Model336HeaterRange.MEDIUM,
                            'HI': Model336HeaterRange.HIGH
                            }
        self.heater_channel = heater_channel

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
        """Returns the output percentage of heater self.heater_channel (in reference to the chosen output range)

        Returns:
            float: output percentage of full scale of current heater range of output channel
        """
        return self.instrument.get_heater_output(self.heater_channel)

    @property
    def get_setpoint(self):
        """Returns the setpoint of output self.heater_channel

        Returns:
            float: setpoint value in kelvin (preferred units of output self.heater_channel)
        """
        return self.instrument.get_control_setpoint(self.heater_channel)

    @property
    def get_heater_range(self):
        """Return current heater range setting of output self.heater_channel

        Returns:
            Model336HeaterRange entry: heater range
        """
        return self.instrument.get_heater_range(self.heater_channel)

    @property
    def get_heater_pid(self):
        """ returns the P, I and D values of the closed loop controler of output self.heater_channel

        :return: tuple of floats (P, I, D)
        """
        _pid_dict = self.instrument.get_heater_pid(self.heater_channel)
        p, i ,d = _pid_dict["gain"], _pid_dict["integral"], _pid_dict["ramp_rate"]
        return (p,i,d)

### Methods

    def connect_ls336(self):
        """conntects to first available ls336 intrument

        Returns:
            intrument class: a class representing the ls336 temperature controler
        """
        return Model336()

    def set_setpoint(self, setpoint):
        """Sets the temperature setpoint of heater output self.heater_channel

        Args:
            setpoint (float): temperature setpoint in Kelvin

        Raises:
            CommunicationFailure: Is raised if temperature setpoint is not set correctly

        Returns:
            float: new temperature setpoint in Kelvin
        """
        self.instrument.set_control_setpoint(self.heater_channel, setpoint)
        sleep(0.1) #wait for controler to set new value
        setpoint_new = self.get_setpoint
        if setpoint_new != setpoint:
            raise CommunicationFailure("Setpoint was not set correctly!")
        return setpoint_new

    def set_heater_range(self,range):
        """sets the heater range to enabele or disable output

        Args:
            range (string): ('OFF', 'LO', 'MID', 'HI') key of dictonary self.heater_range

        Raises:
            CommunicationFailure: Is raised if heater range was not set correctly

        Returns:
            Model336HeaterRange entry: returns entry of IntEnum corresponding to set heater range
        """
        self.instrument.set_heater_range(self.heater_channel, self.heater_range[range])
        sleep(0.1) #wait for controler to set new value
        new_range = self.get_heater_range
        if new_range != self.heater_range[range]:
            raise CommunicationFailure("Heater was not set correctly")
        return new_range

    def set_heater_pid(self, pid_values):
        """sets the pid values of closed loop controller

        Args:
            pid_values (3-tuple of floats): (p_value, i_value, d_value) key of dictionary self.heater_range

        Raises:
            CommunicationFailure: Is raised if heater range was not set correctly

        Returns:
            Model336HeaterRange entry: returns entry of IntEnum corresponding to set heater range
        """
        self.instrument.set_heater_pid(self.heater_channel, pid_values[0],pid_values[1],pid_values[2])
        sleep(0.1) #wait for controler to set new value
        new_pid_values = self.get_heater_pid
        if new_pid_values != pid_values:
            raise CommunicationFailure("PID values were not set correctly")
        return new_pid_values


class CommunicationFailure(Exception):
    pass






