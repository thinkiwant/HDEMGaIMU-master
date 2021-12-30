import threading, socket, PythonSocketServer
import pyqtgraph as pg
import numpy as np
import time
from PythonSocketServer import data, emgReadSign
import PythonSocketServer

VisualOn = True

class emgPlotter(threading.Thread):
    def __init__(self):
        super(emgPlotter, self).__init__()
        self.win = pg.GraphicsLayoutWidget(show=True)
        self.win.setWindowTitle('Scrolling Plots Mode 1')
        print("start plotter thread.%d" % (threading.get_ident()))


    def __del__(self):
        print("end plotter thread.%d" % (threading.get_ident()))

    def run(self) -> None:

        # number of channels
        N = 12
        chanList = [1,4,6,11,15,17,23,25,27,29,34,42,46,48,50,54,57,59,61,63]
        # the length of plot
        L=20
        data1 = np.zeros([L, N])

        P = []
        curve = []
        for i in range(N):
            P.append(self.win.addPlot())
            if (not (i + 1) % 4):
                self.win.nextRow()
            curve.append(P[-1].plot(np.zeros(L)))

        def update1():
            # (see also: np.roll)

            data1[:-1, :] = data1[1:, :]
            data1[-1, :] = PythonSocketServer.data[chanList[0:N]]

            for i in range(N):
                curve[i].setData(data1[:, i])

        while VisualOn:
            update1()
            time.sleep(0.2)
