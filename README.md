# LS336Control

UI to control a Lakeshore 336 temperature controller. 

## Installation and Usage

Install from Github via 
```commandline
pip install git+https://github.com/HammerSeb/LS336Control.git
```

Use as module via
```commandline
python -m ls336
```

This opens a UI window which automatically connects to the next available Lakeshore LS336 controller.

The program is hard coded to use LS336's output 1. 

## Logging
The program automatically creates a log file in hdf5 format named "ls336_log_TIMESTAMP.hdf5" when the live view is started the first time (Start-Button). The save directory can be specified via the button "Set Log Directory". 

The Live view values (Sample/Tip temperature, heater power) are logged with every live View update. Update time can be changed to values between 1s and 3600s. The data sets are stored in the groups "T_sample", "T_tip" and "P_heater" each containing two data sets "time" and "data", storing the time stamps in epoch time and the respective value. 

Every time the temperature set point, the heater range or the PID values are changed, a log entry is generated in the groups "T_set_point", "Heater_mode" and "PID_values". Time stamps are stored in epoch time. 

## Adaptation
If you need to connect to a specific LS336 controller, for example if you have more than one controller connected, adapt the ``` connect_ls336``` function of the ```local_instrument``` class in ```lib.ls_interface```. This function uses the ```Model336``` class to initialize the connection with the controller. Specific parameters can be set to connect to a specific com port. See [lakeshore package documentation](https://lake-shore-python-driver.readthedocs.io/en/latest/model_336.html?highlight=Model336#) for details.

To change the controller heater output, change the ```HEATER_CHANNEL``` variable in the ```main()``` function is ```ui.ls336ui``` python file. 
