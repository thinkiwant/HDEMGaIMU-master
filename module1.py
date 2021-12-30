#!/usr/bin/env python3

import sys, time, imuThread
from PyQt5.Qt import *
from PyQt5 import QtWidgets, uic,QtGui
from PyQt5.QtCore import *
import pyqtgraph as pg
import numpy as np

import PythonSocketServer
from PythonSocketServer import SocketServer
import emgPlotter
from mainwindow2 import Ui_MainWindow

ipPref = '192.168.1.1'
ipList = {ipPref + '1': 0, ipPref + '2': 1, ipPref + '3': 2, ipPref + '4': 3}

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):



    def __init__(self,app, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        super().setWindowTitle("HD sEMG")
        self.app = app
        self.imuPort = 'null'
        self.label.setText("File Name (4 alphabetic characters).")
        self.lcdNumber.display(123456)
        self.N = 16
        self.btn5Status = 0


        self.moduleList = [self.label_4,self.label_6, self.label_8,self.label_10]
        for i in self.moduleList:
            i.setPixmap(QPixmap('off.jpg'))


        defaultFileNamePrfx = 'AAAA'
        self.name = defaultFileNamePrfx
        # Start button
        self.pushButton.setCheckable(True)
        self.pushButton.clicked.connect(self.the_button1_clicked)

        # Stop button
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.setDisabled(True)
        self.pushButton_2.clicked.connect(self.the_button2_clicked)

        # Apply button
        self.pushButton_3.setCheckable(True)
        self.pushButton_3.clicked.connect(self.the_button3_clicked)

        # Test button
        self.pushButton_4.setCheckable(True)
        self.pushButton_4.clicked.connect(self.the_button4_clicked)

        # Display button
        self.pushButton_5.setCheckable(True)
        self.pushButton_5.clicked.connect(self.the_button5_clicked)

        # checkBox
        self.lcdNumber.display(0)

        # Line Edit

        # Recording Time
        self.time = [4, 176]
        self.sckServer = SocketServer(1,fuc = self.updateMStatus, filename = self.name) # set the number of EMG modules
        self.sckServer.setRecordTime(self.time)
        print(ipList)

    def the_button1_clicked(self):
        self.counter = 0
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.timer_behave)
        self.imu()
        self.sckServer.setAcceptDevices(['1','2','3','4'])
        self.sckServer.startRecording()
        self.timer.start()
        #self.imuThread.join()
        self.pushButton.setDisabled(True)
        self.pushButton_2.setDisabled(False)
        self.pushButton_5.setDisabled(True)

    def the_button2_clicked(self):
        self.sckServer.stopRecording()
        self.timer.stop()
        self.imuT.imu.Stop()
        print('Stop recording.')
        self.pushButton.setDisabled(False)
        self.pushButton_2.setDisabled(True)
        self.pushButton_5.setDisabled(False)


    def the_button3_clicked(self):
        name = self.lineEdit.text()
        if name.isalpha() & (len(name)==4):
            self.name = name
            self.sckServer.setFileName(name)


        else:
            print('Invalid name format. Please change another file name.')

    def the_button4_clicked(self):
        com = self.lineEdit_2.text()
        self.imuPort = com

    def the_button5_clicked(self):
        if(self.btn5Status == 0):
            id = self.lineEdit_3.text()
            if id in ['1','2','3','4']:
                self.sckServer.setAcceptDevices([id])
                self.sckServer.startVisualizing()
                emgPlotter.VisualOn = True
                self.WinD = emgPlotter.emgPlotter()
                self.WinD.start()
                self.pushButton_5.setText('Stop displaying')
                self.btn5Status = 1
                self.pushButton.setDisabled(True)

            else:
                print("invalid module number (please enter value:1~4)")
        else:
            PythonSocketServer.emgReadSign = False
            self.sckServer.stopVisualizing()
            self.btn5Status = 0
            self.pushButton_5.setText('Display')
            emgPlotter.VisualOn = False
            self.pushButton.setDisabled(False)



    def apply_fileName(self,s):
        print(s)

    def timer_behave(self):
        self.counter += 1
        self.lcdNumber.display(self.counter)
        if self.counter == self.time[0]*256 + self.time[1]:
            self.the_button2_clicked()

    def updateMStatus(self, ip, state):
        print(ip)
        if ip in ipList:
            if state == 1:
                pic = 'on.jpg'
            elif state == 0:
                pic = 'off.jpg'
            self.moduleList[ipList[ip]].setPixmap(QPixmap(pic))
            self.app.processEvents()
        else:
            print('ip status wasn\'t updated.')

    def imu(self):
        self.imuT = imuThread.imuThread(self.name+'1', self.imuPort)
        self.imuT.start()

from PythonSocketServer import data
if __name__=='__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()
