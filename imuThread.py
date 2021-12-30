import threading, imu

class imuThread(threading.Thread):
    def __init__(self, filename, imuPort):
        threading.Thread.__init__(self)
        self.filename = filename
        self.imu = imu.IMU(filename, imuPort)

    def run(self):
        print("start imu recording.\n")
        self.imu.start()
        print('end imu recording.\n')
