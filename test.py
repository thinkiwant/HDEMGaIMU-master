import threading, time

class myThread(threading.Thread):
    def __init__(self, No, times):
        threading.Thread.__init__(self)
        self.No = No
        self.times = times

    def run(self):
        i = self.times
        while(i>0):
            print('Thread '+str(self.No)+'\n')
            i-=1
        print('Thread ends\n')

if __name__ == '__main__':
    T1 = myThread(1,3)

    T1.start()
    time.sleep(1)
    print('sleep ends\n')
    T1.start()
    while(1):
        pass