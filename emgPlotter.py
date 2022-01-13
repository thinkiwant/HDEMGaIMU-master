import threading
import pyqtgraph as pg
import numpy as np
import time
import PythonSocketServer

VisualOn = True

class emgPlotter(threading.Thread):
    def __init__(self, app):
        super(emgPlotter, self).__init__()
        #self.win = pg.GraphicsLayoutWidget(show=True)
        self.plot = pg.plot()
        self.plot.setWindowTitle('Scrolling Plots Mode 1')
        self.plot.setLabel('bottom', 'Index', units = 'B')
        self.app = app
        print("start plotter thread.%d" % (threading.get_ident()))


    def __del__(self):
        print("end plotter thread.%d" % (threading.get_ident()))

    def run(self) -> None:
        print("emgPlotter initializing starts.")
        nChan = 66
        nPoints = 30
        # number of channels
        # the length of plot

        curves = []
        for idx in range(nChan):
            curve = pg.PlotCurveItem(pen=({'color':(idx, nChan*1.3), 'Width':1}),skipFiniteCheck = True)
            self.plot.addItem(curve)
            curve.setPos(0, idx)
            curves.append(curve)
        print("emgPlotter initializing 1.")
        self.plot.setYRange(0, nChan)
        self.plot.setXRange(0, nPoints)
        #self.plot.resize(600, 900)

        ##self.plot.addItem(rgn)
        print("emgPlotter initializing 2.")

        currentData = np.zeros([nChan, nPoints])
        print("emgPlotter initialized.")
        def update1():
            # (see also: np.roll)
            #print(currentData[:,-1])
            step = 1
            currentData[:, :-1] = currentData[:, 1:]
            currentData[:, -1] = PythonSocketServer.data[0:nChan]*10
            for i in range(nChan):
                #curve[i].setData(self.data[:, i])
#                curves[i].setData([PythonSocketServer.data[i]])
                curves[i].setData(currentData[i])

            self.app.processEvents()

        while VisualOn:
            update1()
            time.sleep(0.05)
