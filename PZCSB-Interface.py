from Tkinter import*
import tkMessageBox
import visa
import ttk
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import time

pzcUSB = 'ASRL1::INSTR'

opmGPIB = 'GPIB0::4::INSTR'

opmOn = False

pzcOn = False

rm = visa.ResourceManager()

if(pzcUSB in rm.list_resources()):
        pzc = rm.open_resource('ASRL1::INSTR')#, constant.VI_ATTR_ASRL_FLOW_CNTRL, constant.VI_ATTR_ASRL_XOFF_CHAR, constant.VI_ATTR_ASRL_XON_CHAR)
        pzc.baud_rate = 19200
        pzc.data_bits = 8
        pzc.Parity = False
        pzc.query_delay = 5
        pzc.write_termination = '\r\n'
        pzc.read_termination = '\r\n'
        pzc.StopBits = 1
        pzc.xoff_char = 10
        pzc.xon_char = 10

        pzcOn = True
        #pzc.timeout= None

if(opmGPIB in rm.list_resources()):
        opm = rm.open_resource(opmGPIB)
        opm.write('U1')
        opmOn = True
        
        
class interfaceMain():
    currentMotor = 0
    def __init__(self,master):
        self.master = master
        self.master.geometry('900x900+50+50')
        self.master.title("PZC-SB Interface")

        self.label1 = Label(self.master,text= 'Welcome to the PZC-SC Interface', fg = 'red').grid(row=1,column=2)
    
        self.button6 = Button(self.master,text = "QUIT", fg = 'blue',command = self.finish).grid(row=6,column=8)

       # control the PZC-SB

        self.motor1Label = Label(self.master, text = 'Please enter the distance for motor 1: ').grid(row=11, column = 1)
        motor1 = StringVar()  
        self.entry1 = Entry(self.master, textvariable = motor1).grid(row=11, column = 2)
        self.motor1Button = Button(self.master, text = "Confirm Movement", fg = 'blue', command = lambda: self.runMotor('1', motor1)).grid(row=11,column=3)
    
        self.motor2Label = Label(self.master, text = 'Please enter the distance for motor 2: ').grid(row=13, column =1 )
        motor2 = StringVar()  
        self.entry2 = Entry(self.master, textvariable = motor2).grid(row=13, column = 2)
        self.motor2Button = Button(self.master, text = 'Confirm movement', fg = 'blue', command = lambda: self.runMotor('2', motor2)).grid(row=13, column=3)

        self.motor3Label = Label(self.master, text = 'Please enter the distance for motor 3: ').grid(row=15, column = 1) 
        motor3 = StringVar()      
        self.entry3 = Entry(self.master, textvariable = motor3).grid(row=15, column = 2)
        self.motor3Button = Button(self.master, text = 'Confirm movement', fg = 'blue', command = lambda: self.runMotor('3', motor3)).grid(row=15, column = 3)

        self.motor6Label = Label(self.master, text = 'Please enter the distance for motor 6: ').grid(row=17, column = 1) 
        motor6 = StringVar()      
        self.entry6 = Entry(self.master, textvariable = motor6).grid(row=17, column = 2)
        self.motor6Button = Button(self.master, text = 'Confirm movement', fg = 'blue', command = lambda: self.runMotor('6', motor6)).grid(row=17, column = 3)

        self.motor7Label = Label(self.master, text = 'Please enter the distance for motor 7: ').grid(row=19, column = 1) 
        motor7 = StringVar()      
        self.entry7 = Entry(self.master, textvariable = motor7).grid(row=19, column = 2)
        self.motor7Button = Button(self.master, text = 'Confirm movement', fg = 'blue', command = lambda: self.runMotor('7', motor7)).grid(row=19, column = 3)

        self.motor8Label = Label(self.master, text = 'Please enter the distance for motor 8: ').grid(row=21, column = 1) 
        motor8 = StringVar()      
        self.entry8 = Entry(self.master, textvariable = motor8).grid(row=21, column = 2)
        self.motor8Button = Button(self.master, text = 'Confirm movement', fg = 'blue', command = lambda: self.runMotor('8', motor8)).grid(row=21, column = 3)
     

        #self.AlignmentLabel = Label(self.master, text = 'Accurate for alignment up to 1% of ideal power level.').grid(row=26, column = 2)
        #self.RoughScanButton = Button(self.master, text = 'Calibrate for maximum power: stage 1(Thorough Scan)', fg = 'blue', command = lambda: self.roughCalibration()).grid(row=24, column = 3)
        #self.RoughScan2Button = Button(self.master, text = 'Calibrate for maximum power: stage 2 (Thorough Scan)', fg = 'blue', command = lambda:self.roughCalibration2()).grid(row = 24, column = 4)
        self.fineTuneButton = Button(self.master, text = 'Calibrate for maximum power alignment (Fine Tune Adjustments Only)', fg = 'blue', command = lambda: self.fineCalibration(False)).grid(row=26, column = 3)
        #self.fineTune2Button = Button(self.master, text = 'Calibrate for maximum power: stage 2 (Fine Tune)', fg = 'blue', command = lambda: self.fineCalibration2(False)).grid(row = 26, column = 4)
        #self.veryFineTuneButton = Button(self.master, text = 'Calibrate for maximum power : stage 1 (Very Fine Tune)', fg = 'blue', command = lambda: self.fineCalibration(True)).grid(row=28, column = 3)
        #self.veryFineTune2Button = Button(self.master, text = 'Calibrate for maximum power : stage 2 (Very Fine Tune)', fg = 'blue', command = lambda: self.fineCalibration2(True)).grid(row = 28, column = 4)

        motorNumber = StringVar()
        self.setUpEntry = Entry(self.master ,textvariable = motorNumber).grid(row = 30, column = 1)
        self.initalSetupButton = Button(self.master, text = 'Inital Setup', fg = 'blue', command = lambda : self.initialize(motorNumber)).grid(row = 30, column = 2)
        

    def initialize(self, mot):
        motor = str(mot.get())
        temp = 0
        paths = [0,0]
        #while(paths[0] != 1 and paths[1] != 1):
        sweepPositive = 4000
        sweepNegative = -8000
        currentPower =  float(self.takePowerMeasurement())
        
        #self.runMotor('3', '-8000')
        
        for j in range(8):
            powerComp = 10000
            print(j)
            for i in range(15):
                    print('powerComp = ' + str(powerComp))
                    print('CurrentPower: '+ str(currentPower))
                    
                    if(powerComp > (currentPower*.90)):
                    #if (True):
                        currentPower = float(self.takePowerMeasurement())     
                        
                        self.runMotor(motor, str(sweepPositive))
                        power1 = float(self.takePowerMeasurement())
                        print('power1 = ' + str(power1))
                        time.sleep(.5)
                        if(power1 < powerComp):
                                self.runMotor(motor, str(-sweepPositive))
                                time.sleep(.5)
                        self.runMotor(motor, str(sweepNegative))
                        power2 = float(self.takePowerMeasurement())
                        print('power2 = ' + str(power2))
                        time.sleep(.5)
                        if(power2 < powerComp):
                                self.runMotor(motor, str(-sweepNegative))
                                time.sleep(.5)                       
                        
                        
                        if(power1 > power2 ):
                                self.runMotor(motor, str(2 * sweepPositive))
                                time.sleep(.5)
                                powerComp = power1
                                print('powerComp = ' + str(powerComp))
                        elif(power2 >power1 ):
                                powerComp = power2
                                print('powerComp = ' + str(powerComp))
                    
            sweepPositive /= 2
            sweepNegative /= 2
            

    def roughCalibration(self):
        tkMessageBox.showinfo('Manual Calibration', 'Please move the motors to approximately the correct position. This will save time and ensure accurate alignment.')
        currentMeasurement = 0.0
        self.runMotor('2', '-10000')
        self.runMotor('3', '-10000')

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        maximum = [0, 0, 0]
        onlyMoveX = stop = False
        history = [0,0,0,0,0,0]
        powerCompliance = 0.0000000001

        for y in range(10):
            if(self.currentMotor != 2):
                    self.currentMotor = 2
                    pzc.write('2MO')
                    pzc.write('2MX2')
                    time.sleep(.7)
            if (y % 2 == 0):
                    print pzc.write('2JA6')
            else:
                    print pzc.write('2JA-6')
            for x in range(20):
                print x
                timeDifference = last_time - time.time() + .75
                last_time = time.time()
                if (timeDifference < 0):
                        timeDifference = 0
                time.sleep(timeDifference)
                power = float(self.takePowerMeasurement())
                if (y % 2 == 1):
                    x_graph = -x
                else:
                    x_graph = x
                ax.scatter(float(x_graph), float(y), float(power), c='r', marker='o')
            print pzc.write('2ST')
            self.runMotor('3', '2000')

        plt.show()
        if (not stop):
                if (maximum == [0,0,0]):
                        tkMessageBox.showinfo('Error', 'No identifiable maximum was found. Please ensure the laser is turned on, and the fibers are close together to start.')
                        return
        self.initialize()
        self.fineCalibration(False)

    def roughCalibration2(self):
        tkMessageBox.showinfo('Manual Calibration', 'Please move the motors to approximately the correct position. This will save time and ensure accurate alignment.')
        currentMeasurement = 0.0
        self.runMotor('7', '-1000')
        self.runMotor('6', '-1000')

        #fig = plt.figure()
        #ax = fig.add_subplot(111, projection='3d')
        maximum = [0, 0, 0]
        onlyMoveX = stop = False
        history = [0,0,0,0,0,0]
        powerCompliance = 0.00000000001
        for x in range(20):
            if (stop == False):
                    if (onlyMoveX == False):
                            for y in range(20):
                                power = float(self.takePowerMeasurement())
                                print [x, y, power]
                                #ax.scatter(float(x), float(y), float(power), c='r', marker='o')
                                if (power > maximum[2] and power > powerCompliance):
                                    powerCompliance = powerCompliance * 2
                                    print powerCompliance
                                    #del history[0]
                                    #history.append(1)
                                    if (power > maximum[2] * 3):
                                        maximum = [x, y, power]
                                        # should stop here
                                        stop = True
                                        break
                                    maximum = [x,y, power]
                                #else:
                                #    del history[0]
                                #    history.append(0)
                                    if (x % 2 == 0 or x == 0):
                                        if(history == [1,1,1,0,0,0]):
                                            self.runMotor('6', '-3000')
                                            onlyMoveX = True
                                            break
                                        else:
                                            self.runMotor('6', '100')
                                    else:
                                        if(history == [1,1,1,0,0,0]):
                                            self.runMotor('6', '3000')
                                            onlyMoveX = True
                                            break
                                        else:
                                            self.runMotor('6', '-100')
                    else:
                        #self.powerSweep('2', 1000, 0.01)
                        print 'shortcut'
                    history = [0,0,0,0,0,0]
                    self.runMotor('7', '100')
        
        if (not stop):
                if (maximum == [0,0,0]):
                        tkMessageBox.showinfo('Error', 'No identifyable maximum was found. Please ensure the laser is turned on, and the fibers are close together to start.')
                        return
                
        self.fineCalibration2(False)
        plt.show()


    def fineCalibration(self, onlyVeryFine):
        
        if(not onlyVeryFine):
                maximum = self.powerSweep('2', 500, 0.01)
                maximum = self.powerSweep('3', 500, 0.01, maximum * .9)
                maximum = self.powerSweep('2', 250, 0.01, maximum * .93)
                maximum = self.powerSweep('3', 250, 0.01, maximum * .96)

                new_maximum = self.powerSweep('2', 100, 0.01)
                if (new_maximum > maximum): maximum = new_maximum
                new_maximum = self.powerSweep('3', 100, 0.01)
                if (new_maximum > maximum): maximum = new_maximum
                new_maximum = self.powerSweep('2', 50, 0.01)
                if (new_maximum > maximum): maximum = new_maximum
                new_maximum = self.powerSweep('3', 50, 0.01)
                if (new_maximum > maximum): maximum = new_maximum

        self.veryFineCalibration()
        tkMessageBox.showinfo('Message', 'Finished Alignment.')

    def fineCalibration2(self, onlyVeryFine):
        
        if(not onlyVeryFine):
                maximum = self.powerSweep('7', 500, 0.01)
                maximum = self.powerSweep('6', 500, 0.01, maximum)
                maximum = self.powerSweep('7', 250, 0.01, maximum)
                maximum = self.powerSweep('6', 250, 0.01, maximum)
                
                new_maximum = self.powerSweep('7', 100, 0.01)
                if (new_maximum > maximum): maximum = new_maximum
                new_maximum = self.powerSweep('6', 100, 0.01)
                if (new_maximum > maximum): maximum = new_maximum
                new_maximum = self.powerSweep('7', 50, 0.01)
                if (new_maximum > maximum): maximum = new_maximum
                new_maximum = self.powerSweep('6', 50, 0.01)
                if (new_maximum > maximum): maximum = new_maximum

        self.veryFineCalibration()
        tkMessageBox.showinfo('Message', 'Finished Alignment.')        
        
    def veryFineCalibration(self):
        self.powerScan('2', 40)
        self.powerScan('3', 40)

        self.powerScan('2', 15)
        self.powerScan('3', 15)

        self.powerScan('2', 5)
        self.powerScan('3', 5)


    def veryFineCalibration2(self):
        self.powerScan('7', 40)

        self.powerScan('6', 40)
        self.powerScan('7', 15)

        self.powerScan('6', 15)
        self.powerScan('7', 5)

        self.powerScan('6', 5)

    def powerScan(self, motor, step):
        history = [-1,-1,-1]
        currentMeasurement = startingPower = float(self.takePowerMeasurement())
        lastMeasurement = 0.0
        maxMeasurement = 0.0
        i = 0
        while (currentMeasurement > lastMeasurement or i < 3):
                if (currentMeasurement > maxMeasurement):
                        maxMeasurement = currentMeasurement

                if (currentMeasurement < lastMeasurement): i += 1
                else:
                        i = 0
                        lastMeasurement = currentMeasurement
                print lastMeasurement
                print currentMeasurement
                print i
                print 'pushing right, motor ' + motor
                self.runMotor(motor, str(step))
                time.sleep(.2)
                
                currentMeasurement = float(self.takePowerMeasurement())
                del history[0]
                history.append(1)
                
        self.runMotor(motor, str(-step*2))        
        if (history != [1,1,1] or startingPower > float(self.takePowerMeasurement())):
                lastMeasurement = 0.0
                i = 0
                while (currentMeasurement > lastMeasurement or i < 3):
                        if (currentMeasurement < lastMeasurement): i += 1
                        else:
                                i = 0
                                lastMeasurement = currentMeasurement
                        print 'pushing left, motor ' + motor
                        self.runMotor(motor, str(-step))
                        time.sleep(.2)
                        
                        currentMeasurement = float(self.takePowerMeasurement())
                self.runMotor(motor, str(step*2))


    def powerSweep(self, motor, step, error, maximum=0.0):
        print 'running one power sweep.' 
        measurement1 = 100.0
        measurement2 = 0.0
        maxMeasurement = 0
        history = [-1,-1,-1]
        while (abs(measurement1 - measurement2) > ((measurement1 + measurement2)*error)/ 2):
                measurement15 = float(self.takePowerMeasurement())
                self.runMotor(motor, str(step))
                time.sleep(.3)
                measurement1 = float(self.takePowerMeasurement())
                print 'measurement1: ' + str(measurement1)

                if (measurement1 > maxMeasurement):
                        print "measurement1 is new max: " + str(measurement1)
                        maxMeasurement = measurement1
                if (measurement15 > maxMeasurement):
                        print "measurement1 is new max: " + str(measurement15)
                        maxMeasurement = measurement15
                self.runMotor(motor, str(-step * 2))
                time.sleep(.3)
                measurement2 = float(self.takePowerMeasurement())
                print 'measurement2: ' + str(measurement2)

                # if we end up at higher level than before, restart
                if (measurement2 > maxMeasurement):
                        print "measurement2 is new max: " + str(measurement2)
                        maxMeasurement = measurement2
                
                if (measurement1 < measurement2 and measurement2 > measurement15):
                        print 'moving left'
                        maxMeasurement = measurement2
                        del history[0]
                        history.append(0)
                elif (measurement1 > measurement2 and measurement1 > measurement15):
                        print 'moving right'
                        del history[0]
                        history.append(1)
                        self.runMotor(motor, str(step*2))
                        time.sleep(.3)
                else:
                        self.runMotor(motor, str(step))
                        break
                currentMeasurement = float(self.takePowerMeasurement())
                if (history[1] + history[2] == 1 and currentMeasurement > maxMeasurement * .9):
                        print "gone back and forth, with decent power reading"
                        break
                

                time.sleep(.2)
        return maximum

    def getCoordinates(self):
        not_done = True
        while(not_done):
                try:
                       x = int(pzc.query('2TP2?').split()[1])
                       not_done = False
                except:
                        k=0
        not_done = True
        while(not_done):
                try:
                        y = int(pzc.query('2TP2?').split()[1])
                        not_done = False
                except:
                        k=0
        return [x, y]

    def wait(self):
        #temp = pzc.query('2TS?')
        temp = '@'
        if(temp == '@' or temp == 'P'):
            time.sleep(.2)
            # = pzc.query('2TS?')
        return True

    # Sets the power meter to query for data in milliwatts and then returns the reading.
    def takePowerMeasurement(self):
        if(opmOn == True):
            measurement = opm.query('D?')
            return str(int(float(measurement) * 100000000000) / 100000000000.0)
        if(opmOn == False):
            tkMessageBox.showinfo('Error', 'Please make sure the Optical Power Meter 1830R is plugged into the computer')

    # input the motor number you want to activate, and the distance it should travel.
    def runMotor(self, number, distance):
        if not isinstance(distance, str):
            distance = distance.get()
        if(self.currentMotor != int(number)):
            self.currentMotor = int(number)
            pzc.write('2MO')
            pzc.write('2MX' + number)
            time.sleep(.7)
        print ('2PR ' + distance)
        pzc.write('2PR ' + distance)
        time.sleep(.003 * abs(int(distance))**.7)

    def finish(self):
        if(pzcOn): pzc.close()
        if(opmOn): opm.close()
        self.master.destroy()

def main():
    root=Tk()
    app = interfaceMain(root)
    root.mainloop()

if __name__ == '__main__':
    main()
