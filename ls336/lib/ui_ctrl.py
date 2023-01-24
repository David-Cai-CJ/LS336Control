from functools import partial
from datetime import datetime
from time import mktime
import h5py
from os.path import join, exists
from PyQt5.QtWidgets import QFileDialog
from ls336.lib.ls_interface import local_intrument
from .. import get_base_path

class ctrl_ui():
    def __init__(self, ui, heater_channel):
        self._ui = ui
        self.global_timestamp = datetime.now()
        self.save_path = get_base_path()
        self.log_file = None
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

        # set logfile path
        self._ui.setSavePath.clicked.connect(self._setLogPath)

        # Start Read out loop
        self._ui.startStop.clicked.connect(partial(self._startStopReadLoop, controller_instance))

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

        self._ui.statusBar.showMessage(f"Log file save path: {self.save_path}")

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

        # plotting values
        _x = [mktime(dt.timetuple()) for dt in self.time_stamp]

        self._ui.liveViewSampleTempPlot.setData(self.sample_temp, x=_x)
        self._ui.liveViewTipTempPlot.setData(self.tip_temp, x=_x)
        self._ui.liveViewHeaterPlot.setData(self.heater_power, x=_x)

        # logging values
        self._logFileUpdate(self.time_stamp[-1],"live_temp", (
            self.sample_temp[-1], self.tip_temp[-1], self.heater_power[-1]
        ))

    def _setLogPath(self):
        """
        Open a QFileDialog to choose save directory for log file. Path is stored in self.save_path
        """
        self.save_path = QFileDialog.getExistingDirectory(self._ui,
                                                  "Choose log file directory",
                                                    directory=get_base_path())

        self._ui.statusBar.showMessage(f"Log file save path: {self.save_path}")

    def _createLogFile(self):
        """
        Creates hdf5 log file at self.save_path if the file does not exist yet.
        The file can store 7e5 data points for each entry (~ 8 days of entries when reading every second)
        The file has the following data entries:
        
        Sample temperature
        group T_sample: time = list of epoch time as floats from datetime.datetime.timestamp()
                        temp = list of floats 
                        
        Tip temperature
        group T_tip:    time = list of epoch time as floats from datetime.datetime.timestamp()
                        temp = list of floats 
        Heater Power
        group P_heater: time = list of epoch time as floats from datetime.datetime.timestamp()
                        temp = list of floats 
                        
        Temperature set point
        group T_set_point:  time = list of epoch time as floats from datetime.datetime.timestamp()
                            set_point = list of floats

        Heater range
        group Heater_mode:  time = list of epoch time as floats from datetime.datetime.timestamp()
                            heater_mode = list of strings: "off","low", "mid", "high"

        PID parameters
        group PID_values:   time = list of epoch time as floats from datetime.datetime.timestamp()
                            p = list of floats
                            i = list of floats
                            d = list of floats

        """
        _creation_timestamp = datetime.now()
        _timestamp_string = f"{_creation_timestamp.date().isoformat()}_{_creation_timestamp.hour}h_{_creation_timestamp.minute}m_{_creation_timestamp.second}s"
        self.log_file = join(self.save_path, f"ls336_log_{_timestamp_string}.hdf5")
        with h5py.File(self.log_file, "w") as f:
            # Live View data
            t_sample_group = f.create_group("T_sample")
            t_sample_group.create_dataset("time", data = [], maxshape=(7e5,), chunks=True)
            t_sample_group.create_dataset("data", data = [], maxshape=(7e5,), chunks=True)

            t_tip_group = f.create_group("T_tip")
            t_tip_group.create_dataset("time", data = [], maxshape=(7e5,), chunks=True)
            t_tip_group.create_dataset("data", data = [], maxshape=(7e5,), chunks=True)

            p_heater_group = f.create_group("P_heater")
            p_heater_group.create_dataset("time", data = [], maxshape=(7e5,), chunks=True)
            p_heater_group.create_dataset("data", data = [], maxshape=(7e5,), chunks=True)

            # Controller Settings
            t_setpoint_group = f.create_group("T_set_point")
            t_setpoint_group.create_dataset("time", data = [], maxshape=(7e5,), chunks=True)
            t_setpoint_group.create_dataset("set_point", data = [], maxshape=(7e5,), chunks=True)

            heater_mode_group = f.create_group("Heater_mode")
            heater_mode_group.create_dataset("time", data = [], maxshape=(7e5,), chunks=True)
            heater_mode_group.create_dataset("heater_mode", data = [], maxshape=(7e5,), chunks=True, dtype="S4")

            pid_values_group = f.create_group("PID_values")
            pid_values_group.create_dataset("time", data = [], maxshape=(7e5,), chunks=True)
            pid_values_group.create_dataset("p", data = [], maxshape=(7e5,), chunks=True)
            pid_values_group.create_dataset("i", data=[], maxshape=(7e5,), chunks=True)
            pid_values_group.create_dataset("d", data=[], maxshape=(7e5,), chunks=True)

    def _logFileUpdate(self,time_stamp,mode,value):
        """
        updates the log file defined in self.log_file by appending the respective lists of values

        :param time_stamp (datetime): time stamp for log entry
        :param mode (string): selects mode write mode. allowed values "live_temp", "set_point", "heater_mode" ,"pid"
        :param value (misc): depending on mode:
                            live_temp: 3-tuple of floats (T_sample, T_tip, Heater_power)
                            set_point: float temperature set point
                            heater_mode: string ("off","low", "mid", "high")
                            pid: 3-tuple of floats (P, I, D)
        """
        with h5py.File(self.log_file, "a") as f:
            if mode == "live_temp":
                for idx, group in enumerate(["T_sample", "T_tip", "P_heater"]):
                    _time = f[f"{group}/time"]
                    _time.resize(_time.shape[0]+1,axis=0)
                    _time[-1] = time_stamp.timestamp()
                    _value = f[f"{group}/data"]
                    _value.resize(_value.shape[0] + 1, axis=0)
                    _value[-1] = value[idx]
            elif mode == "set_point":
                _time = f["T_set_point/time"]
                _time.resize(_time.shape[0] + 1, axis=0)
                _time[-1] = time_stamp.timestamp()
                _value = f["T_set_point/set_point"]
                _value.resize(_value.shape[0] + 1, axis=0)
                _value[-1] = value
            elif mode == "heater_mode":
                _time = f["Heater_mode/time"]
                _time.resize(_time.shape[0] + 1, axis=0)
                _time[-1] = time_stamp.timestamp()
                _value = f["Heater_mode/heater_mode"]
                _value.resize(_value.shape[0] + 1, axis=0)
                _value[-1] = value
            elif mode == "pid":
                _time = f["PID_values/time"]
                _time.resize(_time.shape[0] + 1, axis=0)
                _time[-1] = time_stamp.timestamp()
                for idx, name in enumerate(["p", "i", "d"]):
                    _value = f[f"PID_values/{name}"]
                    _value.resize(_value.shape[0] + 1, axis=0)
                    _value[-1] = value[idx]

    def _getSetPoint(self, controller_instance):
        """
        Gets temperature set point from controller and writes it to ui.setSetPointValue
        :param controller_instance: ls336 controller instance (local_instrument())
        """
        self.temp_setpoint = controller_instance.get_setpoint
        self._ui.setSetPointValue.setValue(self.temp_setpoint)

        if self.log_file != None:
            self._logFileUpdate(datetime.now(), "set_point", self.temp_setpoint)

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


        if self.log_file != None:
            self._logFileUpdate(datetime.now(), "heater_mode", self.heater_mode.name)


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

        if self.log_file != None:
            self._logFileUpdate(datetime.now(), "pid", self.pid_values)

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

    def _startStopReadLoop(self, controller_instance):
        """
        Starts or stops the read loop Qtimer
        """
        _active = self._ui.read_loop.isActive()
        if _active == False:
            self._ui.read_loop.start(self.read_time_interval*1000)
            self._ui.startStop.setText("Stop")
            self._ui.liveViewSampleTemp.enableAutoRange()
            self._ui.liveViewTipTemp.enableAutoRange()
            self._ui.liveViewHeater.enableAutoRange()

            # check if log file exists, and if not create log file
            if self.log_file == None:
                self._createLogFile()
            elif exists(self.log_file) == False:
                self._createLogFile()

            self._getSetPoint(controller_instance)
            self._getHeaterMode(controller_instance)
            self._getPidValues(controller_instance)

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

