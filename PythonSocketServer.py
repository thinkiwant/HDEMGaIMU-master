
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 文件名：server.py

import threading
import socket               # 导入 socket 模块
from struct import *
import time
import numpy
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

emgReadSign = True
ConvFact = 4.8 / 65536

class SocketServer():

    ipPref = '192.168.1.1'
    ipList = {ipPref+'1':0, ipPref+'2':1,ipPref+'3':2,ipPref+'4':3}

    # The first command byte
    GETSET = 0
    FSAMP1 = 0b10
    NCH = 0b11
    MODE = 0

    cmd1 = GETSET*0b10000000 + FSAMP1*0b100000 + NCH*0b1000 + MODE*0b1
    print(cmd1)
    # The second command byte
    HRES = 0
    HPF = 1
    EXT = 0
    TRIG = 0
    REC = 0
    GO = 1
    STOP = 0

    cmd2 = HRES*0b10000000 + HPF*0b1000000 + EXT*0b10000 + TRIG*0b100 + REC*0b10 + GO*0b1
    cmd3 = HRES*0b10000000 + HPF*0b1000000 + EXT*0b10000 + TRIG*0b100 + REC*0b10 + STOP*0b1
    # visualize command
    cmdVO = pack('2B', cmd1, cmd2)
    # stop visualizing
    cmdVF = pack('2B', cmd1, cmd3)

    REC = 1
    TRIG = 0b11
    cmd4 = HRES*0b10000000 + HPF*0b1000000 + EXT*0b10000 + TRIG*0b100 + REC*0b10 + STOP*0b0
    REC = 0
    cmd5 = HRES*0b10000000 + HPF*0b1000000 + EXT*0b10000 + TRIG*0b100 + REC*0b10 + STOP*0b0
    # recording command
    cmdRO = pack('2B', cmd1, cmd4)
    # stop recording command
    cmdRF = pack('2B', cmd1, cmd5)

    # Time Bytes


    ##print(cmd)


    def __init__(self, *args, **kwargs):
        self.s = socket.socket()         # 创建 socket 对象
        self.host = socket.gethostname() # 获取本地主机名
        self.port = 45454    
        print('主机名:',self.host)# 设置端口
        self.s.bind((self.host, self.port))        # 绑定端口
        self.s.listen(5)                 # 等待客户端连接
        self.num = args[0]
        self.ploti = 1
        self.accList = []
        self.list2Accept = []
        self.clientList = []
        self.f = kwargs['fuc']
        self.fileName= kwargs['filename']
        self.time  = pack('2B', 4,176) # first byte: 256 seconds,  second Byte: 1 second

    def __del__(self):
        print("End Socket.")
        self.s.close()

    def setFileName(self, name):
        self.fileName = name
        print('set file name: ', self.fileName)

    def startVisualizing(self):
        global emgReadSign
        emgReadSign = True
        self.sendCommand(self.cmdVO, 1)
        self.readData(self.ploti, self.clientList)

    def startRecording(self):
        self.sendCommand(self.cmdRO, 1)

    def stopRecording(self):
        self.sendCommand(self.cmdRF, 0)
        self.clientList.clear()
        print("End EMG recording.")


    def stopVisualizing(self):
        self.stopRecording()
        self.clientList.clear()
        print("End visualizing.")


    def setRecordTime(self, t):
        self.time = pack('2B', t[0], t[1])

    def setAcceptDevices(self, list2accpet):
        self.list2Accept.clear()
        for i in list2accpet:
            self.list2Accept.append(self.ipPref + i)
        print("set list2accept:")
        print(self.list2Accept)

    def sendCommand(self, cmdB, state = 1):#state: with timestamp or not
        while True:
            if (len(self.accList)==len(self.list2Accept)):
                self.accList.clear()
                break
            c,addr = self.s.accept()     # 建立客户端连接
            ip = addr[0]
            if ip in self.list2Accept:
                if (ip not in self.accList):
                    ModleSig = (self.ipList[ip] + 65).to_bytes(1,byteorder = 'little')
                    print ('连接地址：', ip)
                    print("length of client: %d" % len(self.clientList))
                    self.clientList.append(c)
                    if state == 1:
                        fileNameCode = self.fileName.encode()
                        #timeStamp = self.getTimeStampBytes()
                        cmd = cmdB + self.time + fileNameCode + ModleSig
                    else:
                        cmd = cmdB
                    self.accList.append(ip)
                    self.f(ip, state)
                    c.send(cmd)

                else:
                    print('address already exists:', ip)
            else:
                c.close()                # 关闭连接

    def readData(self,i, cList):
        T = emgModuleLoaderT(cList[i-1])
        T.start()

    def stopReading(self):
        global emgReadSign
        emgReadSign = False
        self.clientList.clear()
        print("End EMG wireless reading.")



    def getTimeStampBytes(self):
        localtime = time.localtime()

        y = localtime[0]-1980
        m = localtime[1]
        d = localtime[2]
        h = localtime[3]
        m = localtime[4]
        s = localtime[5]

        r1 = (y<<1) + (m>>7)
        r2 = ((m&7)<<5) + d
        r3 = (h<<3) + ((m&56)>>3)
        r4 = ((m&7)<<5) + s

        r = pack('4B', r1,r2,r3,r4)
        return r


bufferSize = 2 * 68 * 50
dataFrame = numpy.zeros(bufferSize)
data = numpy.zeros(bufferSize)

class emgModuleLoaderT(threading.Thread):
    def __init__(self, c:socket.socket):
        global bufferSize
        threading.Thread.__init__(self)
        print("start emg reading thread.")
        self.client = c
        self.curvePlotter = curvePlotterT()

    def __del__(self):
        print('end emg reading thread.')


    def run(self) -> None:
        global emgReadSign, dataFrame

        print("start wireless transfer.")
        self.curvePlotter.start()
        while emgReadSign:
            temp = self.client.recv(bufferSize)
            l = len(temp)
            for i in range(l):
                dataFrame[i] = temp[i]
            #print("dataFrame has length of %d" % (l))
        self.client.close()

class curvePlotterT(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("Initialize curvePlotter.")

    def __del__(self):
        print("end curvePlotterT.")

    def run(self) -> None:
        global dataFrame, ConvFact, data
        while emgReadSign:
            secondData = numpy.array(dataFrame).reshape(-1,2*68)
            frameData = secondData[0, :]
            rawData = frameData.reshape(-1,2)
            data = rawData[:,0] * 256 + rawData[:,1]
            idNeg = numpy.where(data>32768, True, False)
            data[idNeg] = data[idNeg] - 65536
            data = data*ConvFact
            #print(data)
            #print("\n")




