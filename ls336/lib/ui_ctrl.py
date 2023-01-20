from functools import partial
from datetime import datetime
import numpy as np
from math import floor

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
import pyqtgraph as pg

from ls336.ui import ls336ui
from ls336.lib.ls_interface import  local_intrument


class ctrl_ui():
    def __init__(self, ui, heater_channel):
        self._ui = ui
        self.global_timestamp = datetime.now()
        self.save_path = None
        self.temp_setpoint = None
        self.heater_mode = None
        self.read_time_interval = 10
        self.pid_values = (0,0,0)

        ### Initializing data array for live plotting (x,4) (x, 0: time stamps, 1: temp tip, 2: temp sample, 3: heater power)
        self.time_stamp = []
        self.tip_temp = []
        self.sample_temp = []
        self.heater_power = []

        # Start up procedure:
        # - connect to ls336 temperature controller
        # - read all set values from instrument and update UI
        self.ls336 = local_intrument(heater_channel)
        self._ui.ls336 = self.ls336
        self.startUp(self.ls336)
        self.connectSignals(self.ls336)

    def connectSignals(self, controller_instance):
        """

        :param controller_instance: ls336 controller instance (local_instrument())
        :return:
        """
        # Temperature set point
        self._ui.setSetPoint.clicked.connect(partial(self._setSetPoint, controller_instance))
        self._ui.setSetPoint.clicked.connect(partial(self._getSetPoint, controller_instance))

        # Heater Setting
        self._ui.setHeaterSettingOff.clicked.connect(partial(self._setHeaterMode,controller_instance,"OFF"))
        self._ui.setHeaterSettingLow.clicked.connect(partial(self._setHeaterMode,controller_instance,"LO"))
        self._ui.setHeaterSettingMid.clicked.connect(partial(self._setHeaterMode,controller_instance,"MID"))
        self._ui.setHeaterSettingHigh.clicked.connect(partial(self._setHeaterMode,controller_instance,"HI"))

        self._ui.setHeaterSettingOff.clicked.connect(partial(self._getHeaterMode, controller_instance))
        self._ui.setHeaterSettingLow.clicked.connect(partial(self._getHeaterMode, controller_instance))
        self._ui.setHeaterSettingMid.clicked.connect(partial(self._getHeaterMode, controller_instance))
        self._ui.setHeaterSettingHigh.clicked.connect(partial(self._getHeaterMode, controller_instance))

        # PID Setting
        self._ui.pidSet.clicked.connect(partial(self._setPidValues, controller_instance))
        self._ui.pidSet.clicked.connect(partial(self._getPidValues, controller_instance))

        # update time
        self._ui.timeIntervalSet.clicked.connect(self._updateUpdateTime)
        self._ui.timeIntervalSet.clicked.connect(self._updateReadLoop)

        # Start Read out loop
        self._ui.startStop.clicked.connect(self._startStopReadLoop)

        # Read out loop
        self._ui.read_loop.timeout.connect(partial(self._readLiveParameters, controller_instance))

    def startUp(self, controller_instance):
        """
        Startup sequence for the remote control of the LS336 temperature controller
        - gets temperature set point from controller and updates UI
        - gets heater mode from controller and updates UI
        - gets PID values for local control loop from controller and updates UI
        - sets update time for read loop to standard value defined in self.read_time_interval
        :param controller_instance: ls336 controller instance (local_instrument())
        """
        self._getSetPoint(controller_instance)
        self._getHeaterMode(controller_instance)
        self._getPidValues(controller_instance)
        self._setUpdateTime(self.read_time_interval)


    def _readLiveParameters(self, controller_instance):
        """
        Gets Temperature values and heater power from controller, writes them into class attributes,
        updates ui labels ui.displaySampleTemp, ui.displayTipTemp, ui.displayHeaterPower,
        updates plots in live view and triggers a log entry.
        :param controller_instance:
        :return:
        """
        # get values from controller
        self.time_stamp.append(datetime.now())
        self.sample_temp.append(controller_instance.get_sample_temperature)
        self.tip_temp.append(controller_instance.get_tip_temperature)
        self.heater_power.append(controller_instance.get_heater_power)

        # writing values to the UI
        self._ui.displaySampleTemp.setText(f"{self.sample_temp[-1]:.3f}")
        self._ui.displayTipTemp.setText(f"{self.tip_temp[-1]:.3f}")
        self._ui.displayHeaterPower.setText(f"{self.heater_power[-1]:.2f}")

        #TODO updating plots

        self._logFileUpdate(self.time_stamp[-1],"live_temp", (
            self.sample_temp[-1], self.tip_temp[-1], self.heater_power[-1]
        ))
    def _logFileUpdate(self,time_stamp, mode,value):
        """
        creates a log file as a npz-file with the following entries:

        Tsample: 2-n-array [time stamps, sample temperature]
        Ttip: 2-n-array [time stamps, tip temperature]
        Pheater: 2-n-array [time stamps, heater power]
        Tset: 2-m-array [time stamps, temperature set point]
        HeaterMode: 2-k-array [time stamps, heater mode]
        Pid: 4-h-array [time stamps, p-value, i-value, d-value]

        :param time_stamp (datetime): time stamp for log entry
        :param mode (string): selects mode write mode. allowed values "live_temp", "set_point", "heater_mode" ,"pid"
        :param value (misc): depending on mode:
                            live_temp: 3-tuple of floats (T_sample, T_tip, Heater_power)
                            set_point: float temperature set point
                            heater_mode: string ("off","low", "mid", "high")
                            pid: 3-tuple of floats (P, I, D)
        """
        pass
    def _getSetPoint(self, controller_instance):
        """
        Gets temperature set point from controller and writes it to ui.setSetPointValue
        :param controller_instance: ls336 controller instance (local_instrument())
        """
        self.temp_setpoint = controller_instance.get_setpoint
        self._ui.setSetPointValue.setValue(self.temp_setpoint)

        #TODO trigger log entry

    def _setSetPoint(self, controller_instance):
        """
        Sets temperature set point of ls336 temperature controller to value specified by ui.setSetPointValue
        :param controller_instance: ls336 controller instance (local_instrument())
        """
        __setpoint = self._ui.setSetPointValue.value()
        controller_instance.set_setpoint(__setpoint)

    def _getHeaterMode(self, controller_instance):
        """
        Gets heater mode from controller and sets respective Button to checked
        :param controller_instance: ls336 controller instance (local_instrument())
        """
        self.heater_mode = controller_instance.get_heater_range
        if self.heater_mode.value == 0:
            self._ui.setHeaterSettingLow.setChecked(False)
            self._ui.setHeaterSettingMid.setChecked(False)
            self._ui.setHeaterSettingHigh.setChecked(False)
            self._ui.setHeaterSettingOff.setChecked(True)
        elif self.heater_mode.value == 1:
            self._ui.setHeaterSettingLow.setChecked(True)
            self._ui.setHeaterSettingMid.setChecked(False)
            self._ui.setHeaterSettingHigh.setChecked(False)
            self._ui.setHeaterSettingOff.setChecked(False)
        elif self.heater_mode.value == 2:
            self._ui.setHeaterSettingLow.setChecked(False)
            self._ui.setHeaterSettingMid.setChecked(True)
            self._ui.setHeaterSettingHigh.setChecked(False)
            self._ui.setHeaterSettingOff.setChecked(False)
        elif self.heater_mode.value == 3:
            self._ui.setHeaterSettingLow.setChecked(False)
            self._ui.setHeaterSettingMid.setChecked(False)
            self._ui.setHeaterSettingHigh.setChecked(True)
            self._ui.setHeaterSettingOff.setChecked(False)

        # TODO trigger log entry


    def _setHeaterMode(self, controller_instance, range):
        """
        Sets heater range of ls336 to range specified by "range"
        :param controller_instance: ls336 controller instance (local_instrument())
        :param range: (string) ("OFF", "LO", "MID", "HI")
        """
        controller_instance.set_heater_range(range)

    def _getPidValues(self, controller_instance):
        """
        Gets P,I and D values from controller and writes it to ui.pValue/iValue/dValue, respectively
        :param controller_instance: ls336 controller instance (local_instrument())
        """
        self.pid_values = controller_instance.get_heater_pid
        self._ui.pValue.setValue(self.pid_values[0])
        self._ui.iValue.setValue(self.pid_values[1])
        self._ui.dValue.setValue(self.pid_values[2])

        # TODO trigger log entry

    def _setPidValues(self, controller_instance):
        """
        sets P,I and D values of controller to values specified in ui.pValue/iValue/dValue, respectively
        :param controller_instance: ls336 controller instance (local_instrument())
        """
        __pid_values = (self._ui.pValue.value(),self._ui.iValue.value(),self._ui.dValue.value())
        controller_instance.set_heater_pid(__pid_values)

    def _setUpdateTime(self, time_interval):
        """
        Sets update time for read loop to time_intervall and updates ui.timeInterval
        :param time_intervall: (float) update time for read loop in seconds
        """
        self.read_time_interval = time_interval
        self._ui.timeInterval.setValue(self.read_time_interval)

    def _updateUpdateTime(self):
        """
        Gets update time from ui.timeInterval
        """
        self.read_time_interval = self._ui.timeInterval.value()

    def _startStopReadLoop(self):
        """
        Starts or stops the read loop Qtimer
        """
        _active = self._ui.read_loop.isActive()
        if _active == False:
            self._ui.read_loop.start(self.read_time_interval*1000)
            self._ui.startStop.setText("Stop")
        else:
            self._ui.read_loop.stop()
            self._ui.startStop.setText("Start")

    def _updateReadLoop(self):
        """
        Updates the read loop time interval to value self.read_time_interval
        :return:
        """
        self._updateUpdateTime()
        self._ui.read_loop.setInterval(self.read_time_interval*1000)

