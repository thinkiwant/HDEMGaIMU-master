# coding:UTF-8
import serial, os, re, string

class IMU():
    def __init__(self, filename = 'imu', imuPort = 'null'):
        self.RecordingSign = True
        self.ACCData = [0.0] * 8
        self.GYROData = [0.0] * 8
        self.AngleData = [0.0] * 8
        self.PortData = [0.0] * 8

        self.FrameState = 0  # 通过0x后面的值判断属于哪一种情况
        self.Bytenum = 0  # 读取到这一段的第几位
        self.CheckSum = 0  # 求和校验位

        self.a = tuple([0.0] * 3)
        self.w = tuple([0.0] * 3)
        self.Angle = tuple([0.0] * 3)
        self.Port = tuple([0.0] * 3)
        self.imuPort = imuPort
        self.fileName = filename


    def DueData(self, inputdata, f):  # 新增的核心程序，对读取的数据进行划分，各自读到对应的数组里
        #FrameState = self.FrameState # 在局部修改全局变量，要进行global的定义
        #Bytenum = self.Bytenum
        #CheckSum = self.CheckSum
        #a = self.a
        #w = self.w
        Angle = self.Angle
        Port = self.Port
        for data in inputdata:  # 在输入的数据进行遍历
            # data = ord(data)
            if self.FrameState == 0:  # 当未确定状态的时候，进入以下判断
                if data == 0x55 and self.Bytenum == 0:  # 0x55位于第一位时候，开始读取数据，增大bytenum
                    self.CheckSum = data
                    self.Bytenum = 1
                    continue
                elif data == 0x51 and self.Bytenum == 1:  # 在byte不为0 且 识别到 0x51 的时候，改变frame
                    self.CheckSum += data
                    self.FrameState = 1
                    self.Bytenum = 2
                elif data == 0x52 and self.Bytenum == 1:  # 同理
                    self.CheckSum += data
                    self.FrameState = 2
                    self.Bytenum = 2
                elif data == 0x53 and self.Bytenum == 1:
                    self.CheckSum += data
                    self.FrameState = 3
                    self.Bytenum = 2
                elif data == 0x55 and self.Bytenum == 1:
                    self.CheckSum += data
                    self.FrameState = 4
                    self.Bytenum = 2
            elif self.FrameState == 1:  # acc    #已确定数据代表加速度

                if self.Bytenum < 10:  # 读取8个数据
                    self.ACCData[self.Bytenum - 2] = data  # 从0开始
                    self.CheckSum += data
                    self.Bytenum += 1
                else:
                    if data == (self.CheckSum & 0xff):  # 假如校验位正确
                        self.a = get_acc(self.ACCData)
                    self.CheckSum = 0  # 各数据归零，进行新的循环判断
                    self.Bytenum = 0
                    self.FrameState = 0
            elif self.FrameState == 2:  # gyro

                if self.Bytenum < 10:
                    self.GYROData[self.Bytenum - 2] = data
                    self.CheckSum += data
                    self.Bytenum += 1
                else:
                    if data == (self.CheckSum & 0xff):
                        self.w = get_gyro(self.GYROData)
                    self.CheckSum = 0
                    self.Bytenum = 0
                    self.FrameState = 0
            elif self.FrameState == 4:  # port
                if self.Bytenum < 10:
                    self.PortData[self.Bytenum - 2] = data
                    self.CheckSum += data
                    self.Bytenum += 1
                else:
                    if data == (self.CheckSum & 0xff):
                        self.Port = get_port(self.PortData)
                        d = self.a + self.w + (self.Port,)
                        for i in d:
                            f.write(str(i)+'\t')
                        f.write('\n')
                    self.CheckSum = 0
                    self.Bytenum = 0
                    self.FrameState = 0
            else:
                if self.Bytenum < 10:
                    #self.GYROData[self.Bytenum - 2] = data
                    self.CheckSum += data
                    self.Bytenum += 1
                else:
                    self.CheckSum = 0
                    self.Bytenum = 0
                    self.FrameState = 0

    def start(self):
        self.RecordingSign = True
        # use raw_input function for python 2.x or input function for python3.x
        # port = raw_input('please input port No. such as com7:')
        if self.imuPort=='null':
            port = input('please input port No. such as com7:')
        else:
            port = self.imuPort
        #baud = int(input('please input baudrate(115200 for JY61 or 9600 for JY901):'))
        baud = 115200
        ser = serial.Serial(port, baud, timeout=0.5)  # ser = serial.Serial('com7',115200, timeout=0.5)
        print(ser.is_open)

        unlock = 'ffaa6988b5'
        UnlockByte = bytes.fromhex(unlock)
        retainConfig = 'ffaa000000'
        RetainConfigByte = bytes.fromhex(retainConfig)
        returnRate = 'ffaa030b00'
        ReturnRateByte = bytes.fromhex(returnRate)
        returnedContent = 'ffaa022600'
        ContentByte = bytes.fromhex(returnedContent) # 0x51 acc 0x52 gyro 0x55 port
        portMode = 'ffaa100100'
        PortModeByte = bytes.fromhex(portMode)
        ser.write(UnlockByte)
        ser.write(ContentByte)
        ser.write(ReturnRateByte)
        ser.write(PortModeByte)
        ser.write(RetainConfigByte)

        while(os.path.exists(self.fileName+'.txt')):
            prefix = re.findall(r'(\D+)\d+.*',self.fileName)[0]
            self.fileName = prefix + str(int(re.findall(r'\D+(\d+)\D*',self.fileName)[0])+1)
        with open(self.fileName+'.txt', 'w', encoding='utf-8') as f:
            column = ['ax(g)', 'ay(g)', 'az(g)', 'wx(deg/s)', 'wy(deg/s)', 'wz(deg/s)', 'D2']
            for i in column:
                f.write(i + '\t')
            f.write('\n')
            while (self.RecordingSign != False):
                datahex = ser.read(33)
                self.DueData(datahex, f)

        ser.close()

    def setFileName(self, filename):
        self.fileName = filename

    def Stop(self):
        self.RecordingSign = False


def get_acc(datahex):
    axl = datahex[0]
    axh = datahex[1]
    ayl = datahex[2]
    ayh = datahex[3]
    azl = datahex[4]
    azh = datahex[5]

    k_acc = 16.0

    acc_x = (axh << 8 | axl) / 32768.0 * k_acc
    acc_y = (ayh << 8 | ayl) / 32768.0 * k_acc
    acc_z = (azh << 8 | azl) / 32768.0 * k_acc
    if acc_x >= k_acc:
        acc_x -= 2 * k_acc
    if acc_y >= k_acc:
        acc_y -= 2 * k_acc
    if acc_z >= k_acc:
        acc_z -= 2 * k_acc

    return acc_x, acc_y, acc_z


def get_gyro(datahex):
    wxl = datahex[0]
    wxh = datahex[1]
    wyl = datahex[2]
    wyh = datahex[3]
    wzl = datahex[4]
    wzh = datahex[5]
    k_gyro = 2000.0

    gyro_x = (wxh << 8 | wxl) / 32768.0 * k_gyro
    gyro_y = (wyh << 8 | wyl) / 32768.0 * k_gyro
    gyro_z = (wzh << 8 | wzl) / 32768.0 * k_gyro
    if gyro_x >= k_gyro:
        gyro_x -= 2 * k_gyro
    if gyro_y >= k_gyro:
        gyro_y -= 2 * k_gyro
    if gyro_z >= k_gyro:
        gyro_z -= 2 * k_gyro
    return gyro_x, gyro_y, gyro_z


def get_angle(datahex):
    rxl = datahex[0]
    rxh = datahex[1]
    ryl = datahex[2]
    ryh = datahex[3]
    rzl = datahex[4]
    rzh = datahex[5]
    k_angle = 180.0

    angle_x = (rxh << 8 | rxl) / 32768.0 * k_angle
    angle_y = (ryh << 8 | ryl) / 32768.0 * k_angle
    angle_z = (rzh << 8 | rzl) / 32768.0 * k_angle
    if angle_x >= k_angle:
        angle_x -= 2 * k_angle
    if angle_y >= k_angle:
        angle_y -= 2 * k_angle
    if angle_z >= k_angle:
        angle_z -= 2 * k_angle

    return angle_x, angle_y, angle_z


def get_port(datahex):
    #d0l = datahex[0]
    #d0h = datahex[1]
    #d1l = datahex[2]
    #d1h = datahex[3]
    d2l = datahex[4]
    d2h = datahex[5]
    #d3l = datahex[6]
    #d3h = datahex[7]
    vcc = 3.5

    #d0 = (d0h << 8 | d0l)
    #d1 = (d1h << 8 | d1l)
    d2 = (d2h << 8 | d2l)
    #d3 = (d3h << 8 | d3l)

    return d2





if __name__ == '__main__':
    imu1 = IMU('file1')
    imu1.start()