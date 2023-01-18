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
        self.global_timestamp = None
        self.save_path = None
        self.temp_setpoint  = None
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

    def connectSignals(self, controller_instance):
        pass

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
        pass

    def _getSetPoint(self, controller_instance):
        """
        Gets temperature set point from controller and writes it to ui.setSetPointValue
        :param controller_instance: ls336 controller instance (local_instrument())
        """
        self.temp_setpoint = controller_instance.get_setpoint
        self._ui.setSetPointValue.setText(f"{self.temp_setpoint:.2f}")

    def _setSetPoint(self, controller_instance):
        pass

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


    def _setHeaterMode(self, controller_instance):
        pass

    def _getPidValues(self, controller_instance):
        """
        Gets P,I and D values from controller and writes it to ui.pValue/iValue/dValue, respectively
        :param controller_instance: ls336 controller instance (local_instrument())
        """
        self.pid_values = controller_instance.get_heater_pid
        self._ui.pValue.setText(self.pid_values[0])
        self._ui.iValue.setText(self.pid_values[1])
        self._ui.dValue.setText(self.pid_values[2])

    def _setPidValues(self, controller_instance):
        pass

    def _setUpdateTime(self, time_interval):
        """
        Sets update time for read loop to time_intervall and updates ui.timeInterval
        :param time_intervall: (float) update time for read loop in seconds
        """
        self.read_time_interval = time_interval
        self._ui.timeInterval.setText(self.read_time_interval)

    def _startReadLoop(self):
        pass

    def _stopReadLoop(self):
        pass

    def _updateReadLoop(self):
        pass

