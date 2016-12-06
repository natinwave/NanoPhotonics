from Tkinter import*
from tkFileDialog import askopenfilename
import tkMessageBox
import visa
import ttk
import os
from time import sleep
from math import*
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
from collections import deque
import subprocess

# we are using pyvisa to establish connections between gpib, rs232, and usb cables and the computer.
# by running the following commands, we are able to establish a connection with the devices connected
# and get their serial/gpib addresses.
# import visa
# rm = visa.ResourceManager()
# rm.list_resources()
# to "connect" a device, write the following line : deviceName = rm.open_resource('GPIB#::#::INSTR') for gpib or deviceName = rm.open_resource('ASRL#::INSTR') for usb and rs232 devices.
# please refer to a referance manual for the correct commands to send the device.
# reading, or querying information from the device : deviceName.query('commandName')
# writing information to the device: deviceName.write('commandName')


# aq is the AQ4321A, gpib id is 20
# aqd is the AQ4321D gpib id is 24
# opm is the Optical Power Meter, Newport 1830C gpib is 8
# sa is the spectrum analyzer gpib id is 4
# lm is hte lightwave multimeter gpib id is 19
#eco1 is the device that controls the x y and z coordinates of the gantry system
# pollux controls the rotation of the gantry system

rm = visa.ResourceManager()

#flags to check to make sure that the devices are properly connected to the computer
cancel = aqOn = aqdOn = opmOn = saOn = lmOn = eco1On = polluxOn = opmrOn = False

aq = aqd = opm = sa = lm = eco1 = pollux = opmr = None

eco1Queue = deque()

def findAddress(query, response, connection, baudrate=None):
        print rm.list_resources()
        for resource in reversed(rm.list_resources()):
            if connection in resource:
                temp = rm.open_resource(resource)
                if baudrate != None: temp.baud_rate = baudrate
                print resource
                try:
                    print temp.query(query)
                    if (response in temp.query(query)):
                        temp.close()
                        return resource
                    else:
                        temp.close()
                except:
                    temp.close()
        return ''

def connect():
    address1 = findAddress('identify', 'Corvus Eco 1 456 1 200', 'ASRL', 57600)
    address2 = findAddress('1 nidentify', 'Pollux 1 411 1 0', 'ASRL1', 19200)
    
    if (address1 != '' and address2 != ''):
        global eco1On, eco1, polluxOn, pollux
        eco1On = True
        polluxOn = True
        pollux = rm.open_resource(address2)
        pollux.baud_rate = 19200
        pollux.write('2.0 1 setpitch ')
        eco1 = rm.open_resource(address1)
        eco1.baud_rate = 57600

        return True
    return False

#class to control the gantry crane
class Gantry:
    current_position = [0.0, 0.0, 0.0]
    qLimit = [0.0, 0.0, 0.0]
    pause_queue = False

    def __init__(self,master):
        try:
            if(not cancel):
                pollux.query('1 getpitch ')
                eco1.write("cal ")
                self.wait()
                qLimit = eco1.query('-1 pos ').split()
                qLimit[0] = float(qLimit[0])
                qLimit[1] = float(qLimit[1])
                qLimit[2] = float(qLimit[2])
        except:
            tommy = 'cool'
                
        #sets up the window, calibrate the xyz movement to start at (0,0,0)
        self.master = master
        self.master.geometry('1300x950+50+50')
        self.master.title('Gantry System')
        self.button1 = Button(self.master, text = "QUIT", fg = 'blue',command = self.quitGantry).grid(row=6,column=20)


        # allows the user to traverse the x plane in mm
        self.x_coor = Label(self.master,  text = 'Please enter x coordinate').grid(row=6, column = 1)
        x_input = DoubleVar()
        self.x_entry_box = Entry(self.master, textvariable = x_input).grid(row=6, column =2)
        self.x_distance_label = Label(self.master, text = "mm").grid(row = 6, column = 3)
        self.x_button2 = Button(self.master, text = "Run", fg = 'blue', command = lambda: self.runX(x_input)).grid(row = 6, column = 4)

        # allows the user to traverse the y plane in mm
        self.y_coor = Label(self.master,  text = 'Please enter y coordinate').grid(row=8, column = 1)
        y_input = DoubleVar()
        self.y_entry_box = Entry(self.master, textvariable = y_input).grid(row=8, column =2)
        self.y_distance_label = Label(self.master, text = "mm").grid(row = 8, column = 3)
        self.y_button2 = Button(self.master, text = "Run", fg = 'blue', command = lambda: self.runY(y_input)).grid(row = 8, column = 4)

        # allows the user to traverse the z plane in mm
        self.z_coor = Label(self.master,  text = 'Please enter z coordinate').grid(row=10, column = 1)
        z_input = DoubleVar()
        self.z_entry_box = Entry(self.master, textvariable = z_input).grid(row=10, column =2)
        self.z_distance_label = Label(self.master, text = "mm").grid(row = 10, column = 3)
        self.z_button2 = Button(self.master, text = "Run", fg = 'blue', command = lambda: self.runZ(z_input)).grid(row = 10, column = 4)

        # allows the user to traverse the x plane in micrometers
        self.xmicro = Label(self.master, text = 'Please enter the x coordinate').grid(row=6, column = 6)
        x_input2 = DoubleVar()
        self.xMicroBox = Entry(self.master, textvariable = x_input2).grid(row = 6, column = 7)
        self.xMicroLabel = Label(self.master, text = "um").grid(row=6, column = 8)
        self.xMicroButton = Button(self.master, text = "Run", fg = 'blue', command = lambda : self.xMicro(x_input2)).grid(row=6,column=9)

        # allows the user to traverse the y plane in micrometers
        self.ymicro = Label(self.master, text = 'Please enter the y coordinate').grid(row=8, column = 6)
        y_input2 = DoubleVar()
        self.yMicroBox = Entry(self.master, textvariable = y_input2).grid(row = 8, column = 7)
        self.yMicroLabel = Label(self.master, text = "um").grid(row=8, column = 8)
        self.yMicroButton = Button(self.master, text = "Run", fg = 'blue', command = lambda : self.yMicro(y_input2)).grid(row=8,column=9)

        # allows the user to traverse the z plane in micrometers
        self.zmicro = Label(self.master, text = 'Please enter the z coordinate').grid(row=10, column = 6)
        z_input2 = DoubleVar()
        self.zMicroBox = Entry(self.master, textvariable = z_input2).grid(row = 10, column = 7)
        self.zMicroLabel = Label(self.master, text = "um").grid(row=10, column = 8)
        self.zMicroButton = Button(self.master, text = "Run", fg = 'blue', command = lambda : self.zMicro(z_input2)).grid(row=10,column=9)


        #working on a way to inpux linear equations for the device to run
        equation = StringVar()
        self.equation_label = Label(self.master, text = 'Please enter equation in terms of x, y, and z.').grid(row=19, column = 1)
        self.equation_box = Entry(self.master, textvariable = equation).grid(row = 19, column = 2)
        

        self.x_label = Label(self.master, text = 'Please enter the upper x bound in millimeters : ').grid(row=20,column=1)
        upperX = DoubleVar()
        self.xBox = Entry(self.master, textvariable = upperX).grid(row=20,column=2)
        self.y_label = Label(self.master, text = 'Please enter the upper y bound in millimeters: ').grid(row=21,column=1)
        upperY = DoubleVar()
        self.yBox = Entry(self.master, textvariable = upperY).grid(row=21,column=2)
        self.z_label = Label(self.master, text = 'Please enter the upper z bound in millimeters: ').grid(row=22,column=1)
        upperZ = DoubleVar()
        self.zBox = Entry(self.master, textvariable = upperZ).grid(row=22,column=2)

        self.stepLabel = Label(self.master, text = 'Please enter the step amount in millimeters: ').grid(row=23, column =1)
        functionStep = DoubleVar()
        self.stepBox = Entry(self.master, textvariable = functionStep).grid(row=23,column=2)
        self.equation_button = Button(self.master, text = "Run Function", fg = 'blue', command = lambda : self.runFunction(equation,functionStep, upperX, upperY, upperZ)).grid(row=19,column=3)

        #allows the user to have access over the rotation
        self.r_coor = Label(self.master,  text = 'Please enter rotation').grid(row=12, column = 1)
        r_input = DoubleVar()
        self.r_entry_box = Entry(self.master, textvariable = r_input).grid(row=12, column =2)
        self.r_distance_label = Label(self.master, text = "degrees").grid(row = 12, column = 3)
        self.r_button2 = Button(self.master, text = "Run", fg = 'blue', command = lambda: self.runR(r_input)).grid(row = 12, column = 4)

        #move the position to a specified one.
        self.moveMMAllButton = Button(self.master, text = "Move all axis to specified position (mm)", fg = 'blue', command = lambda: self.runAllMM(x_input, y_input, z_input, r_input)).grid(row = 14, column = 1)
        self.moveUMAllButton = Button(self.master, text = "Move all axis to specified position (um)", fg = 'blue', command = lambda: self.runAllUM(x_input2, y_input2, z_input2, r_input)).grid(row=16, column = 1)

        #reset the coordinates to (0,0,0)
        self.resetCoordinates = Button(self.master, text = "Reset coordinates to start up spot", fg = 'blue', command = lambda: self.resetPosition()).grid(row = 18, column = 1)


        #scanning square in millimeters
        self.square_size_label = Label(self.master, text = 'Please enter the width of the square in millimeters').grid(row=31, column = 1)
        squareSize = DoubleVar()
        self.square_size_box = Entry(self.master, textvariable = squareSize).grid(row = 31, column = 2)
        self.square_step_label = Label(self.master, text = 'Please enter the step size for the square in millimeters').grid(row=33, column = 1)
        squareStep = DoubleVar()
        self.square_step_box = Entry(self.master, textvariable = squareStep).grid(row = 33, column = 2)
        self.dataPointsLabel = Label(self.master, text = 'Please enter the amount of data points per line').grid(row=35, column = 1)
        numberOfPoints = IntVar()
        self.dataPointsBox = Entry(self.master, textvariable = numberOfPoints).grid(row = 35, column = 2)
        
        self.scan_square_button = Button(self.master, text = "Run Scanning square", fg = 'blue', command = lambda : self.scanSquareMM(squareSize, squareStep, numberOfPoints)).grid(row=36,column=1)

        #scanning square in micrometers
        self.square_size_label = Label(self.master, text = 'Please enter the width of the square in micrometers').grid(row=37, column = 1)
        square_size = DoubleVar()
        self.square_size_box = Entry(self.master, textvariable = square_size).grid(row = 37, column = 2)
        self.square_step_label = Label(self.master, text = 'Please enter the step size for the square in micrometers').grid(row=39, column = 1)
        square_step = DoubleVar()
        self.square_step_box = Entry(self.master, textvariable = square_step).grid(row = 39, column = 2)
        self.scan_square_button = Button(self.master, text = "Run Scanning square", fg = 'blue', command = lambda : self.scanSquareUM(square_size, square_step)).grid(row=40,column=1)

        fileName = StringVar()
        self.fileNameBox = Entry(self.master, textvariable = fileName).grid(row = 43, column = 4)
        self.saveMakroButton = Button(self.master, text = "Save Makro to file: ", fg = 'red', command = lambda: self.saveMakro(fileName)).grid(row=43, column=3)

        self.runFileButton = Button(self.master, text = "Run Makro from file", fg = 'red', command = lambda: self.runMakroFromFile()).grid(row=45, column=3)


        self.OPMRLabel = Label(self.master, text = 'Please specify the units for the optical power meter as \'dBm\' or \'mW\': ').grid(row = 47, column = 1)

        opmrUnits = StringVar()
        self.OPMREntry = Entry(self.master, textvariable = opmrUnits).grid(row = 47, column = 2)
        self.turnOnOPMRButton = Button(self.master, text = 'Turn On 1830-R Optical Power Meter', fg = 'blue', command = lambda: self.turnOn1830R(opmrUnits)).grid(row = 47, column =3)
        self.turnOffOPMRButton = Button(self.master, text = 'Turn Off the 1830-R Optical Power Meter', fg = 'blue', command = lambda: self.turnOff1830R()).grid(row = 47, column = 4)
        powerFileName = StringVar()
        self.savePowerFileLabel = Entry(self.master, textvariable = powerFileName).grid(row = 49, column = 4)
        self.savePowerFileButton = Button(self.master, text = 'Save power readings to File', fg = 'red', command = lambda: self.savePowerFile(powerFileName)).grid(row = 49, column = 3)
        self.clearPowerFile = Button(self.master, text = 'Clear Power File Measurements', fg = 'blue', command = lambda : self.clearFile()).grid(row = 47, column = 5)
        self.readingsHelpLabel = Button(self.master, text = 'Help', fg = 'blue', command = lambda : self.readingsHelp()).grid(row = 47, column = 6)

        self.displayGraphButton = Button(self.master, text = 'Display Graph From File', fg = 'blue', command = lambda : self.displayGraphFromFile()).grid(row = 49, column = 6)

        self.getLargestPowerLevel = Button(self.master, text = 'Get power level and location', fg = 'blue', command = lambda: self.getLargestLevel()).grid(row = 49, column = 5)

        self.pauseQueueButton = Button(self.master, text = "Begin Building Macro", fg = 'blue', command = lambda: self.pauseQueue()).grid(row=60, column=1)
        self.runQueueButton = Button(self.master, text = "Run Macro", fg = 'blue', command = lambda: self.startQueue()).grid(row=62, column = 1)
        self.makroHelpButton = Button(self.master, text = "Makro Help", fg = 'blue', command = lambda: self.makroHelp()).grid(row=64, column = 1)

        if (cancel):
            self.master.destroy()   
        else:
            self.id = self.master.after(100, self.runEco1Queue) #runs the command queue periodically

    def turnOn1830R(self, opmrUnits):
        global opmrOn, opmr    
        if('GPIB0::4::INSTR' in rm.list_resources()):
            opmrOn = True
            opmr = rm.open_resource('GPIB0::4::INSTR')
        if(opmrOn == True):
            units = opmrUnits.get()
            if(units == 'mW'):    
                opmr.write('U1')
                with open('PowerMeasurement.txt', 'w'): pass
                powerFile = open('PowerMeasurement.txt', "a")
                powerFile.write("The units for coordinates are in nanometers \n")
                powerFile.write("The units for power are in mW \n")
                powerFile.close()
                
            elif(units == 'dBm'):
                opmr.write('U3')
                with open('PowerMeasurement.txt', 'w'): pass
                powerFile = open('PowerMeasurement.txt', "a")
                powerFile.write("The units for coordinates are in nanometers \n")
                powerFile.write("The units for power are in dBm \n")
                powerFile.close()
                
            else:
                tkMessageBox.showinfo("Error", "Please enter the correct units")
        if(opmrOn != True):
                tkMessageBox.showinfo("Error", "The device was not properly connected, please unplug and try again")
                
    def turnOff1830R(self):
            global opmrOn
            if(opmrOn == False):
                    tkMessageBox.showinfo("Error", "The 1830-R is already turned off")
            elif(opmrOn == True):
                    opmrOn = False
            print(opmrOn)

    def savePowerFile(self, name_input):
            if (isinstance(name_input, str)):
                    name = name_input
            else:
                    name = name_input.get()
            print name[-4:]
            if (name[-4:] != '.txt'):
                    name = name + '.txt'
            #file = open('PowerMeasurement.txt', "w")
            os.rename('PowerMeasurement.txt', name)

            #file.close()
                    
    def takeMeasurement(self):
            global opmr
            powerFile = open('PowerMeasurement.txt', "a")
            measurement = opmr.query('D?')
            xCoord = self.current_position[1]
            yCoord = self.current_position[2]
            zCoord = self.current_position[0]

            powerFile.write('The measurement at: ' + str(xCoord) + ' ' + str(yCoord) + ' '+ str(zCoord) + ' is ' + str(measurement) )
            powerFile.close()

    def clearFile(self):
        with open('PowerMeasurement.txt', 'w'): pass

    def getLargestLevel(self):
            xList = []
            yList = []
            zList = []
            powerReadings = []
            x=0
            y=0
            z=0
            units = ''
            file = open('PowerMeasurement.txt', 'r')
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            for line in file:
                    words = line.split()
                    if(words[-1] == 'dBm'):
                        units = 'dBm'
                    if(words[-1] == 'mW'):
                        units = 'mW'
                    if(words[-1] != 'nanometers' and words[-1] != 'dBm' and words[-1] != 'mW'):
                            powerReadings.append(words[-1])
                            xList.append(words[-5])
                            yList.append(words[-4])
                            zList.append(words[-3])
                            print [float(words[-5]), float(words[-4]), float(words[-1])]
                            ax.scatter(float(words[-5]), float(words[-4]), float(words[-1]), c='r', marker='o')
            
            powerReadings = map(float, powerReadings)
            maxPower = max(powerReadings)
            xList = map(float, xList)
            yList = map(float, yList)
            zList = map(float, zList)
            file.close()
            file=open('PowerMeasurement.txt', 'r')
            for line in file:
                    if(str(maxPower) in line):
                            words = line.split()
                            x = words[-5]
                            y = words[-4]
                            z = words[-3]
            
            self.xLabel = Label(self.master, text ='X Coordinate = ' + str(x)).grid(row = 49, column = 1)
            self.yLabel = Label(self.master, text = 'Y Coordinate = ' + str(y)).grid(row = 49, column = 2)
            self.zLabel = Label(self.master, text = 'Z Coordinate = ' + str(z)).grid(row = 49, column = 3)
            self.maxPowerLabel = Label(self.master, text = str(maxPower)).grid(row = 49, column = 4)

            ax.set_xlabel('X (nanometers)')
            ax.set_ylabel('Y (nanometers)')
            ax.set_zlabel('Power (' + str(units) + ')')
            plt.show()
            file.close()

    def readingsHelp(self):
            tkMessageBox.showinfo("Welcome to the help window", "When using the power readings, you must specify the units before clicking \'turn on device\' (mW or dBm). \n \n After turning on the power meter, anytime you move the gantry system, the power readings at that location will be written to a file on the desktop called \'PowerMeasurement.txt\'. The units will displayed at the top. \n\n To save the file to a different name (and to protect it from being deleted or overwritten by accident), enter a new file name in the lower entry box and press the \'Save Power Readings to File\' button. \n \n To clear the file, you can either type in a different unit into the turn on box or click the clear file button. (This will only clear the \'PowerMeasurement.txt\' file. Any file you've saved will not be affected.) \n \n Clicking the get power level button will go through the current PowerMeasurement.txt file and pick out the highest power level. It will then display that level along with the coordinates those values are at.")


    def saveMakro(self, name_input):
        if (isinstance(name_input, str)):
            name = name_input
        else:
            name = name_input.get()
        file = open(name + '.txt', "w")
        file.write('beginmakro \n')
        
        for i in range(len(eco1Queue)):
                if (eco1Queue[i][1] == 'w'):
                        file.write(eco1Queue[i][0] + '\n')

        file.write('endmakro')
        file.close()

    def runMakroFromFile(self):
        file_name = askopenfilename() # show an "Open" dialog box and return the path to the selected file
        file = open(file_name, 'r')
        file.readline()

        for line in file:
                print line
                if ('endmakro' not in line):
                        eco1Queue.append([line, 'w'])
        file.close()

    def makroHelp(self):
        tkMessageBox.showinfo('Makro Help', 'Pressing the \'Begin Building Makro\' button will pause the execution of all motor commands, and begin recording them in a queue. \n\nYou can then continue entering any new commands as you normally would, but instead of being run immediately, they will be stored. \n\nWhen finished, pressing the \'Run Makro\' button will empty the command queue, executing all the commands in the order you entered them (This will NOT save the makro). \n\nPressing the \'Save Makro to File\' button will save a new .txt file with all of the commands you\'ve entered. You can read and/or edit this .txt file, and then select \'Run Makro from File\' to run all of the commands in the order they were originally entered.')

    def displayGraphFromFile(self):
        xList = yList = zList = powerReadings = []
        x=y=z=0
        units = ''
         
        file_name = askopenfilename() # show an "Open" dialog box and return the path to the selected file
        file = open(file_name, 'r')
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        for line in file:
                words = line.split()
                if(words[-1] == 'dBm'):
                    units = 'dBm'
                if(words[-1] == 'mW'):
                    units = 'mW'
                if(words[-1] != 'nanometers' and words[-1] != 'dBm' and words[-1] != 'mW'):
                        ax.scatter(float(words[-5]), float(words[-4]), float(words[-1]), c='r', marker='o')
        
        file.close()
        ax.set_xlabel('X (nanometers)')
        ax.set_ylabel('Y (nanometers)')
        ax.set_zlabel('Power (' + str(units) + ')')
        plt.show()

    def runFunction(self, equation, increment, upperX, upperY, upperZ):
   
        eq = equation.get()

        upperX = upperX.get()
        if (upperX <= 0 or upperX > 103):
            upperX = 103
        upperY = upperY.get()
        if (upperY <= 0 or upperY > 28):
            upperY = 28
        upperZ = upperZ.get()
        if (upperZ <= 0 or upperZ > 103):
            upperZ = 103
        increment = increment.get()
        if(increment <= 0):
                increment = .1
        import parser
        dependant = 'y'
        if ('=' in eq):
            dependant = eq[0]
            eq = eq[eq.find('=') + 1:]
        code = parser.expr(eq).compile()

        independant = ''

        if('x' in eq):
                independant = 'x'
        elif('y' in eq):
                independant = 'y'
        elif('z' in eq):
                independant = 'z'

        eq = eq.replace('sin', '')
        eq = eq.replace('cos', '')
        eq = eq.replace('sqrt', '')

        for i in range(len(eq)):
                if (eq[i] != independant and eq[i].isalpha()):
                        tkMessageBox.showinfo("Error", "Please enter a function with only one independant variable.")
                        return

        x = y = z = x_dif = y_dif = z_dif = 0.0

        if('x' in eq):
            x_dif = increment
        elif('y' in eq):
            y_dif = increment
        elif('z' in eq):
            z_dif = increment

        # Increments independent variable by increment size
        while (self.qLimit[1] <= upperX and self.qLimit[1] > -.001 and self.qLimit[2] < upperY and self.qLimit[2] > -.001 and self.qLimit[0] <= upperZ and self.qLimit[0] > -.001):

            eco1Queue.append(['%.4f ' % z_dif + ' ' + '%.4f' % x_dif + ' ' + '%.4f' % y_dif + ' r ', 'w'])
            self.qLimit = [z_dif + self.qLimit[0], x_dif + self.qLimit[1], y_dif + self.qLimit[2]]

            if('x' in eq):
                x = increment + x
            elif('y' in eq):
                y = increment + y
            elif('z' in eq):
                z = increment + z

            if (dependant == 'y'):
                y_dif = eval(code) - y
                y = eval(code)
            elif (dependant == 'z'):
                z_dif = eval(code) - z    
                z = eval(code)
            elif(dependant == 'x'):
                x_dif = eval(code) - x
                x = eval(code)

            print eval(code)

        


    #runX allows the user to move the gantry system in the x direction
    #has code to make sure the user does not overstep the bounds when trying to move system
    #units for this are in mm
    def runX(self, x_input):
        if(isinstance(x_input,float)):
           x = x_input
        elif (isinstance(x_input,int)):
           x = float(x_input)
        else:
           x = x_input.get()

        print 'x: ' + str(x)

        if(x + self.qLimit[1] >= -.0001 and x + self.qLimit[1] <= 103.48883):
          eco1Queue.append(['0 ' + '%.4f' % x + ' 0 r ', 'w'])
          self.qLimit[1] += x

        else:
            tkMessageBox.showinfo("Error", "The value you entered is not in the range for the X movement")

    #runY allows the user to move the gantry system in the y direction
    #has code to make sure the user does not overstep the bounds when trying to move system
    #units for this are in mm
    def runY(self, y_input):
        if(isinstance(y_input,float)):
           y = y_input
        else:
           y = y_input.get()

        print 'y: ' + str(y)
        if (y + self.qLimit[2] >= -.0001 and y + self.qLimit[2] <= 28):
            eco1Queue.append(['0 0 ' + '%.4f' % y + ' r ', 'w'])
            self.qLimit[2] += y
        else:
            tkMessageBox.showinfo("Error", "The value you entered is not in the range for the Y movement")

    #runZ allows the user to move the gantry system in the z direction
    #has code to make sure the user does not overstep the bounds when trying to move system
    #units for this are in mm
    def runZ(self, z_input):

        if(isinstance(z_input, float)):
                z = z_input
        else:
                z = z_input.get()

        if (z + self.qLimit[0] >= -.0001 and z + self.qLimit[0] <= 103):
            eco1Queue.append(['%.4f' % z + ' 0 0 r ', 'w'])
            self.qLimit[0] = self.qLimit[0]+ z
        else:
            tkMessageBox.showinfo("Error", "The value you entered is not in the range for the Z movement")

    #takes the users input and moves in degrees
    def runR(self, r_input):
        r = r_input.get()
        pollux.write('%.4f' % r + ' 1 ' + ' nr ')

    #moves the gantry system to a specified location in milimeters.
    def runAllMM(self, x_input, y_input, z_input, r_input):
            x = x_input.get()
            y = y_input.get()
            z = z_input.get()
            r = r_input.get()
            pollux.write('%.4f' % r + ' 1 ' + ' nr ')
            eco1Queue.append(['%.4f ' % z + '%.4f ' % x + '%.4f ' % y + ' move ', 'w'])
            self.getCoordinates()

    #xMicro allows the user to move the gantry system in the x direction
    #has code to make sure the user does not overstep the bounds when trying to move system
    #units for this are in micrometers
    def xMicro(self, x_input2):

            if(isinstance(x_input2, float)):
                    x = x_input2 / 1000
            else:
                    x = x_input2.get() / 1000


            if(x + self.qLimit[1] >= -.0001 and x + self.qLimit[1] <= 103.48883):
              eco1Queue.append(['0 ' + '%.4f' % x + ' 0 r ', 'w'])
              self.qLimit[1] = self.qLimit[1] + x

            else:
                tkMessageBox.showinfo("Error", "The value you entered is not in the range for the X movement")


    #yMicro allows the user to move the gantry system in the y direction
    #has code to make sure the user does not overstep the bounds when trying to move system
    #units for this are in micrometers
    def yMicro(self, y_input2):

            if(isinstance(y_input2, float)):
                    y = y_input2 / 1000
            else:
                    y = y_input2.get() / 1000
            
            if (y + self.qLimit[2] >= -.0001 and y + self.qLimit[2] <= 28):
                eco1Queue.append(['0 0 ' + '%.4f' % y + ' r ', 'w'])
                self.qLimit[2] = self.qLimit[2] + y
            else:
                tkMessageBox.showinfo("Error", "The value you entered is not in the range for the Y movement")
            
 

    #zMicro allows the user to move the gantry system in the z direction
    #has code to make sure the user does not overstep the bounds when trying to move system
    #units for this are in micrometers
    def zMicro(self, z_input2):

            if(isinstance(z_input2, float)):
                    z = z_input2 / 1000
            else:
                    z = z_input2.get() / 1000

            if (z + self.qLimit[0] >= -.0001 and z + self.qLimit[0] <= 103):
                eco1Queue.append(['%.4f' % z + ' 0 0 r ', 'w'])
                self.qLimit[0] = self.qLimit[0] + z
            else:
                tkMessageBox.showinfo("Error", "The value you entered is not in the range for the Z movement")


    #moves the gantry position to a specified location in micrometers
    def runAllUM(self, x_input2, y_input2, z_input2, r_input):
            x = x_input2.get() / 1000
            y = y_input2.get() / 1000
            z = z_input2.get() / 1000
            r = r_input.get() / 1000
            pollux.write('%.4f' % r + ' 1 ' + 'nr ')
            eco1Queue.append(['%.5f ' % z + '%.5f ' % x + '%.5f ' % y + 'move ','w'])
            print(eco1.query('-1 pos').split())
            self.getCoordinates()

    #displays on the gantry window the x,y,z coordinates in millimeters
    def getCoordinates(self):

            self.current_position = eco1.query('-1 pos ').split()
            
            i = 0
            while (len(self.current_position) != 3 and i < 10):
                self.wait()
                i += 1
                self.current_position = eco1.query('-1 pos ').split()
            if (i == 10):
                tkMessageBox.showinfo("Error", "The controller is sending invalid position data. Please restart the device.")
                self.quitGantry()
            self.x = Label(self.master, text = str(self.current_position[1]) + " x ").grid(row=29,column=1)
            self.y = Label(self.master, text = str(self.current_position[2]) + " y ") .grid(row=29,column = 2)
            self.z = Label(self.master, text = str(self.current_position[0]) + " z ").grid(row=29,column=3)
            self.current_position[0] = float(self.current_position[0])
            self.current_position[1] = float(self.current_position[1])
            self.current_position[2] = float(self.current_position[2])

    def scanSquareMM(self, size_in, step_in, points):
            if(points.get() <=2):
                numberOfPoints = 2
            else:                    
                numberOfPoints = points.get()
            step = step_in.get() 
            size = size_in.get() 
         
            print numberOfPoints
            print step
            print size

            self.getCoordinates()
            stepCounter = 0
            sizeLimit = float(self.current_position[1]) + size
            xStarting = float(self.current_position[1])
            yStarting = float(self.current_position[2])
            xPlot = [xStarting]
            yPlot = [yStarting]         


            #self.qLimit = [0, xStarting, yStarting]
            
            if(sizeLimit < 0 or sizeLimit > 103.4883):
                tkMessageBox.showinfo("error", "your box could not be computed because it is out of bounds")
            if(size + yStarting > 28.4 or size + yStarting < 0):
                   tkMessageBox.showinfo("error", "the y direction is too large")
            else:

                    for i in range(numberOfPoints):
                            if(i % 2 == 0):
                                if(self.qLimit[2] > 28.42532 or self.qLimit[2] < 0):
                                   break
                                else:
                                   for k in range(numberOfPoints - 1):
                                           eco1Queue.append(['0 '+ '%.4f ' % (float(size)/float(numberOfPoints - 1))  + ' 0 r ', 'w'])
                                           self.qLimit[1] += (float(size)/float(numberOfPoints - 1))
                                           xPlot.append(self.qLimit[1])
                                           yPlot.append(self.qLimit[2])

                                   if (i < numberOfPoints - 1):        
                                           eco1Queue.append(['0 0 '  + '%.4f ' % (float(size)/float(numberOfPoints - 1)) + ' r ', 'w'])
                                           self.qLimit[2] += (float(size)/float(numberOfPoints - 1))

                                           xPlot.append(self.qLimit[1])
                                           yPlot.append(self.qLimit[2])

                            if(i % 2 != 0):
                                if(self.qLimit[2] > 28.42532 or self.qLimit[2] < 0):
                                   break
                                else:
                                   for k in range(numberOfPoints - 1):
                                           eco1Queue.append(['0 '+ '%.4f ' % (-float(size)/float(numberOfPoints - 1))  + ' 0 r ', 'w'])
                                           self.qLimit[1] -= (float(size)/float(numberOfPoints - 1))
                                           xPlot.append(self.qLimit[1])
                                           yPlot.append(self.qLimit[2])

                                   if (i < numberOfPoints - 1):         
                                           eco1Queue.append(['0 0 '  + '%.4f ' % (float(size)/float(numberOfPoints - 1)) + ' r ', 'w'])
                                           self.qLimit[2] += (float(size)/float(numberOfPoints - 1))
                                           xPlot.append(self.qLimit[1])
                                           yPlot.append(self.qLimit[2])

                    eco1Queue.append(['0 0 0 r', 'w'])
                    plt.axis([-size - 1, size + 1, -size - 1 , size + 1])
                    print(len(xPlot))
                    print(len(yPlot))
                    plt.grid(True)
                    plt.plot(xPlot, yPlot)
                    plt.show()


    def scanSquareUM(self, size_in, step_in):
            step = step_in.get()/ 1000
            size = size_in.get() / 1000
            self.current_position = eco1.query('-1 pos ').split()
            stepCounter = 0
            sizeLimit = float(self.current_position[1]) + size
            xStarting = float(self.current_position[1])
            yStarting = float(self.current_position[2])
            k = 0
            incrementor = int(size/step)
            #print incrementor
            if(sizeLimit < 0 or sizeLimit > 103.4883):
                tkMessageBox.showinfo("error", "your box could not be computed because it is out of bounds")
            if(size + yStarting > 28.4):
                   tkMessageBox.showinfo("error", "the y direction is too large")
            else:

                    for i in range(incrementor):
                            if(i %2 == 0):
                                    
                                if((stepCounter + yStarting) > 28.42532 or (stepCounter + yStarting) < 0):
                                   break
                                else:
                                   eco1Queue.append(['0 '+ '%.4f ' % (size + xStarting)  + '%.4f ' % (stepCounter + yStarting) + ' move ', 'w'])
                                   self.wait()
                                   stepCounter += step
                                   eco1Queue.append(['0 '+ '%.4f ' % (size + xStarting)  + '%.4f ' % (stepCounter + yStarting) + ' move ', 'w'])
                                   self.wait()
                                   #print(eco1.query('-1 pos').split())
                            if(i %2 != 0):
                                    
                                if((stepCounter + yStarting) > 28.42532 or (stepCounter + yStarting) < 0):
                                   break
                                else:
                                   eco1Queue.append(['0 '+ '%.4f ' % (-size + xStarting)  + '%.4f ' % (stepCounter + yStarting) + ' move ', 'w'])
                                   self.wait()
                                   stepCounter += step
                                   eco1Queue.append(['0 '+ '%.4f ' % (-size + xStarting)  + '%.4f ' % (stepCounter + yStarting) + ' move ', 'w'])
                                   self.wait()
                                   #print(eco1.query('-1 pos').split())                        
    
    #this function waits to make sure that the eco is finished whatever it is doing before returning
    def wait(self):
            status = "1"
            while ("0" not in status):
                try:
                        status = eco1.query('st ')
                except:
                        print 'wait timeout.'

    #resets the position to (0,0,0).  queries the current position to make sure that it is at the 0 position.
    def resetPosition(self):
            pollux.write('1 ncal ')
            eco1.write("clear ")
            eco1.write('0 0 0 move ')
            self.getCoordinates()
            self.qLimit[0] = 0.0
            self.qLimit[1] = 0.0
            self.qLimit[2] = 0.0
            print(eco1.query("-1 pos"))

    def pauseQueue(self):
            self.pause_queue = True

    def startQueue(self):
            self.pause_queue = False

    def runEco1Queue(self):
            global eco1On, eco1, polluxOn, pollux, opmrOn, app

            if (self.pause_queue == False):
                    eco1Queue.append(0)
                    item = eco1Queue.popleft()

                    if (item != 0):
                        eco1Queue.pop()
                        try:
                            self.wait()
                            print "finished waiting, there is an item."
                            if(opmrOn == True):
                                try:
                                    self.takeMeasurement()
                                except:
                                    print "taking measurements is not working."
                            self.runEco1Item(item[0], item[1])
                            print(self.current_position)

                        except:
                            eco1Queue.appendleft(item)
                            tkMessageBox.showinfo('Error', 'Something went wrong running a command, please restart the program and make sure all devices are connected properly. Any unexecuted commands will be saved in RECOVERY.txt.')
                            self.saveMakro('RECOVERY')
                            eco1On = polluxOn = False
                            eco1Queue.clear()
                            self.quitGantry()
                            return
                    else:
                        try:
                            self.wait()
                            self.getCoordinates() #Once queue is done, refreshes the virtual position qLimit to the actual gantry position to ensure accuracy.
                        except:
                            tkMessageBox.showinfo('Error', 'Something went wrong, please restart the program and make sure all devices are connected properly. Any unexecuted commands will be saved in RECOVERY.txt.')
                            self.saveMakro('RECOVERY')
                            eco1On = polluxOn = False
                            eco1Queue.clear()
                            self.quitGantry()
                            return

                        self.qLimit[1] = float(self.current_position[1])
                        self.qLimit[2] = float(self.current_position[2])
                        self.qLimit[0] = float(self.current_position[0])
                    if (item != 0):
                        self.id = self.master.after(10, self.runEco1Queue)
                    else:
                        self.id = self.master.after(2000, self.runEco1Queue)

    def runEco1Item(self, string, command):
            print(string)
            if (command == 'w'):
                    eco1.write(string)
                    new_position = [0, 0, 0]
                    print string.split()
                    if ('r' in string):
                        new_position[0] = self.current_position[0] + float(string.split()[0])
                        new_position[1] = self.current_position[1] + float(string.split()[1])
                        new_position[2] = self.current_position[2] + float(string.split()[2])
                        string = str(new_position[0]) + ' ' + str(new_position[1]) + ' ' + str(new_position[2]) + ' m '
                    elif ('m' in string):
                        new_position[0] = float(string.split()[0])
                        new_position[1] = float(string.split()[1])
                        new_position[2] = float(string.split()[2])
                    self.wait()
                    self.getCoordinates()
                    print new_position
                    print self.current_position
                    i=0
                    while ((abs(new_position[0] - self.current_position[0]) > .1 or abs(new_position[1] - self.current_position[1]) > .1 or abs(new_position[2] - self.current_position[2]) > .1) and i < 5):
                        eco1.write('clear ')
                        eco1.write(string)
                        self.getCoordinates()
                        print 'got coordinates again: '
                        print self.current_position
                        i = i + 1
            elif (command == 'r'):
                    eco1.read(string)
            elif (command == 'q'):
                    eco1.query(string)

            self.wait()
            eco1.write('clear ')

    #quits the gantry window, clears the stack of commands, and resets the device.
    def quitGantry(self):
        plt.close()
        eco1.write("clear ")
        eco1.write("reset ")
        eco1.close()
        pollux.close() 
        self.master.destroy()

cancel = False
while (not connect()):
    if not tkMessageBox.askretrycancel('Error', 'Please connect and power on both the Corvus Eco and the SMC-Pollux.'):
        cancel = True
        break

def main():
    root=Tk()
    app = Gantry(root)
    root.mainloop()

if __name__ == '__main__':
    main()
