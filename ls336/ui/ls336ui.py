import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow 
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

from .. import get_base_path
from ..lib.ui_ctrl import ctrl_ui

class ls336_control(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(get_base_path(),"ui",'ls336ui.ui'),self)
        self.read_loop = QTimer()
        self.read_loop.stop()
        self.defineLiveViewLayout()


    def defineLiveViewLayout(self):
        ### set live view properties
        self.liveViewSampleTemp = self.liveView.addPlot(0,0)
        self.liveViewSampleTemp.getAxis('left').setWidth(80)
        self.liveViewTipTemp = self.liveView.addPlot(1,0)
        self.liveViewTipTemp.getAxis('left').setWidth(80)
        self.liveViewHeater = self.liveView.addPlot(2,0)
        self.liveViewHeater.getAxis('left').setWidth(80)



        # Sample Temperature plot
        self.liveViewSampleTemp.setLabel('left', 'T Sample [K]')
        self.liveViewSampleTemp.setXLink(self.liveViewHeater)

        self.liveViewSampleTempPlot = self.liveViewSampleTemp.plot(pen = 'r')
        self.liveViewSampleTemp.setAxisItems({"bottom": pg.DateAxisItem()})
        SampleTempXAxis = self.liveViewSampleTemp.getAxis('bottom')
        # SampleTempXAxis.setPen(255,255,255,0)
        SampleTempXAxis.setStyle(showValues = False)
        self.liveViewSampleTemp.showGrid(x=True, y=True, alpha=0.5)

        # Tip Temperature plot
        self.liveViewTipTemp.setLabel('left', 'T Tip [K]')
        self.liveViewTipTemp.setXLink(self.liveViewHeater)

        self.liveViewTipTempPlot = self.liveViewTipTemp.plot(pen='b')
        self.liveViewTipTemp.setAxisItems({"bottom": pg.DateAxisItem()})
        TipTempXAxis = self.liveViewTipTemp.getAxis('bottom')
        # TipTempXAxis.setPen(255, 255, 255, 0)
        TipTempXAxis.setStyle(showValues=False)
        self.liveViewTipTemp.showGrid(x=True, y=True, alpha=0.5)

        # Heater power plot
        self.liveViewHeater.setLabel('left', 'Heater [%]')
        # self.liveViewHeater.setLimits(yMin=-0.05)
        self.liveViewHeater.setXLink(self.liveViewHeater)
        self.liveViewHeaterPlot = self.liveViewHeater.plot(pen='g')
        self.liveViewHeater.setAxisItems({"bottom": pg.DateAxisItem()})
        tempXHeater = self.liveViewHeater.getAxis('bottom')
        tempXHeater.setStyle(showValues = True)
        # tempXHeater.setPen(255,255,255,0)
        self.liveViewHeater.showGrid(x = True, y = True, alpha = 0.5)



    def closeEvent(self, event):
        self.read_loop.stop()

def main():
    HEATER_CHANNEL = 1
    ls336 = QApplication(sys.argv)
    gui = ls336_control()
    gui.show()
    ctrl_ui(gui, HEATER_CHANNEL) #initializes controler
    sys.exit(ls336.exec())
    print("debug finished")