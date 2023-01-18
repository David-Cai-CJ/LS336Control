import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow 
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
from qdarkstyle import load_stylesheet_pyqt5

from ls336 import get_base_path
from ls336.lib.ui_ctrl import ctrl_ui

class ls336_control(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(get_base_path(),'ls336ui.ui'))
        self.read_loop = QTimer()
        self.read_loop.stop()
        self.defineLiveViewLayout()

        # controler_instance
        self.ls336 = None

    def defineLiveViewLayout(self):
        ### set live view properties
        self.liveViewTemp = self.liveView.addPlot(0,0)
        self.liveViewTemp.getAxis('left').setWidth(50)
        self.liveViewHeater = self.liveView.addPlot(1,0)
        self.liveViewHeater.getAxis('left').setWidth(50)
        # Temperature plot
        self.liveViewTemp.setLabel('left', 'Temp. [K]')
        self.liveViewTemp.setXLink(self.liveViewValve)
        self.liveViewTemp.showGrid(x = True, y = True, alpha = 0.5)
        tempXAxis = self.liveViewTemp.getAxis('bottom')
        tempXAxis.setPen(255,255,255,0)
        tempXAxis.setStyle(showValues = False)
        # Heater power plot
        self.liveViewHeater.setLabel('left', 'Heater [V]')
        self.liveViewHeater.setLimits(yMin=-0.05)
        self.liveViewHeater.setXLink(self.liveViewValve)
        tempXHeater = self.liveViewHeater.getAxis('bottom')
        tempXHeater.setStyle(showValues = False)
        tempXHeater.setPen(255,255,255,0)
        self.liveViewHeater.showGrid(x = True, y = True, alpha = 0.5)
        
def main():
    HEATER_CHANNEL = 1
    ls336 = QApplication(sys.argv)
    ls336.setStyleSheet(load_stylesheet_pyqt5)
    gui = ls336_control()
    gui.show()
    ctrl_ui(gui, HEATER_CHANNEL) #initializes controler
    sys.exit(ls336.exec())