
from Tkinter import*
from tkFileDialog import askopenfilename
import tkMessageBox
import visa
import ttk
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
aqOn = aqdOn = opmOn = saOn = lmOn = eco1On = polluxOn = opmrOn = keOn = tdON= False

aq = aqd = opm = sa = lm = eco1 = pollux = opmr = ke = td = None

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

class gpibMain():

    #defines the initial window that will be set up when the interface is running
    def __init__(self,master):
        self.master = master
        self.master.geometry('900x900+50+50')
        self.master.title("GPIB Interface")

        self.label1 = Label(self.master,text= 'Welcome to the GPIB Interface', fg = 'red').grid(row=1,column=2)
        self.button1 = Button(self.master,text = "Go To AQ4321A", fg = 'blue', command = self.gotoAQA).grid(row=6,column=1)
        self.button2 = Button(self.master,text = "Go To AQ4321D", fg = 'blue', command = self.gotoAQD).grid(row=6,column=2)
        self.button3 = Button(self.master,text = "Go To Optical Power Meter 1830-C", fg = 'blue', command = self.gotoOPM).grid(row=6,column=3)
        self.opm1830RButton = Button(self.master,text = "Go To Optical Power Meter 1830-R", fg = 'blue', command = self.gotoOPM_1830R).grid(row=7,column=3)
        self.button4 = Button(self.master,text = "Spectrum Analyzer", fg = 'blue', command = self.gotoSA).grid(row=6,column=4)
        self.button5 = Button(self.master,text = "Go To Lightwave Multimeter", fg = 'blue', command = self.gotoLM).grid(row=6,column=5)
        self.gantryButton = Button(self.master,text = "Gantry System", fg = 'blue', command = self.gotoGantry).grid(row=6,column=6)
        self.button6 = Button(self.master,text = "QUIT", fg = 'blue',command = self.finish).grid(row=6,column=7)
        self.keithbutton = Button(self.master, text = 'Go To Keithly', command = self.gotoKeithley).grid(row = 2, column = 1)
        self.tdsButton = Button(self.master, text = 'Go to TDS', command = self.gotoTDS).grid(row= 2, column = 2)
    #go to functions each bring up a new window which holds the operations and functions of the separate devices.
    #checks to see if the device is connected, if so brings up a window, if not, flashes error message.
    def gotoAQA(self):
        address = findAddress('*IDN?', 'ANDO-ELECTRIC/AQ4321A/00113110/HOST0A.02.11.00/SUB0A.02.14.00/LD0A.01.01.00', 'GPIB')
        if (address != ''):
            global aqOn, aq
            aqOn = True
            aq = rm.open_resource(address)
            root2 = Toplevel(self.master)
            myGUI = AQA(root2)
        else:
            tkMessageBox.showinfo('Error', 'Please connect the AQ4321A to the computer with a GPIB cable.')

    def gotoAQD(self):
        address = findAddress('*IDN?', 'ANDO-ELECTRIC/AQ4321D/00985946/HOST0D.02.11.00/SUB0D.02.14.00/LD0D.01.01.00', 'GPIB')
        if (address != ''):
            global aqdOn, aqd
            aqdOn = True
            aqd = rm.open_resource(address)
            root3 = Toplevel(self.master)
            myGUI = AQD(root3)
        else:
            tkMessageBox.showinfo('Error', 'Please connect the AQ4321D to the computer with a GPIB cable.')
    def gotoOPM(self):
        if('GPIB0::8::INSTR' in rm.list_resources()):
            global opmOn, opm
            opmOn = True
            opm = rm.open_resource('GPIB0::8::INSTR')
            root4 = Toplevel(self.master)
            myGUI = OPM(root4)
        else:
            tkMessageBox.showinfo("Error", "Please connect the Newport 1830-C Optical Power Meter and set the GPIB address to 8.")

    def gotoOPM_1830R(self):
        proc = subprocess.Popen('start /B C:\Users\Public\Desktop\(x86)NewportPowerMeterApplication.LNK', shell=True)
        proc.wait()

    def gotoSA(self):
        if(saOn == True):
            root5 = Toplevel(self.master)
            myGUI = SA(root5)
        else:
            tkMessageBox.showinfo("Error", "The Spectrum Analyzer is not connected")

    def gotoLM(self):
        address = findAddress('*IDN?', 'Agilent Technologies,8163B,DE48204524,V5.04(63796)', 'GPIB')
        lm = rm.open_resource('GPIB0::19::INSTR')
        print(lm.query('*IDN?'))
        if(address !=''):
            global lmOn, lm
            lmOn = True
            lm = rm.open_resource(address)
            root6= Toplevel(self.master)
            myGUI = LM(root6)
        
        else:
            tkMessageBox.showinfo("Error", "The Lightwave Multimeter is not connected")

    def gotoGantry(self):
    
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
            root7 = Toplevel(self.master)
            myGUI = Gantry(root7)
        else:
            tkMessageBox.showinfo("Error", "Both the Corvus Eco and Pollux need to be connected to manage the Gantry System.")

    def gotoKeithley(self):
            address = findAddress('*IDN?', 'KEITHLEY INSTRUMENTS INC.,MODEL 2400,900142?,C24   Feb 14 2002 11:59:45/A02  /J/H', 'GPIB')
            if(address != ''):
                    global keOn, ke
                    keOn = True
                    ke = rm.open_resource(address)
                    root8 = Toplevel(self.master)
                    myGUI = KEITH(root8)
    def gotoTDS(self):
            address = findAddress('*IDN?', 'TEKTRONIX,TDS 784A,0,CF:91.1CT FV:v4.2.1e', 'GPIB')
            if(address != ''):
                    global tdOn, td
                    tdOn = True
                    td = rm.open_resource(address)
                    td.timeout = 200000
                    td.chunk_size = 102400
                    root9 = Toplevel(self.master)
                    myGUI = TDS(root9)

    #when you quit the interface, the devices are each disconnected from the pc controls
    def finish(self):
        try: 
            if (aqOn): aq.close() 
            if(aqdOn): aqd.close()
            if (opmOn): opm.close()
            if (saOn): sa.close()
            if (lmOn): lm.close()
            if (eco1On): eco1.close()
            if (polluxOn): pollux.close()
            if (tdOn) : td.close()
            if(keOn): ke.close()
        except:
            tkMessageBox.showinfo('Error', 'Please do not disconnect any devices until after the program has been closed.')

        self.master.destroy()
class TDS():
    def __init__(self,master):
            
        self.master = master
        self.master.geometry('800x800+150+150')
        self.master.title('TDS OSCILOSCOPE')
        self.quitTDS = Button(self.master, text = 'Quit', fg = 'blue', command = self.quitTD).grid(row = 4, column = 3)
        self.channelLabel = Label(self.master, text = 'This function will query the data in channel one and display it as a graph', fg = 'red').grid(row = 1, column = 1)

        
        self.dataPointLabel = Label(self.master, text = 'Please enter the amount of data points').grid(row = 2, column = 1)
        dpNumber = StringVar()
        self.dpEntry = Entry(self.master, textvariable = dpNumber).grid(row = 2, column = 2)

        self.timeDivisionLabel = Label(self.master, text = 'Please enter the time per division: ').grid(row = 3, column =1)
        tdNumber = DoubleVar()
        self.tdEntry = Entry(self.master, textvariable = tdNumber).grid(row= 3, column = 2)
        self.tdTimeLabel = Label(self.master, text = 'seconds').grid(row =3, column = 3)
        self.tdButton = Button(self.master, text = 'Confirm time per division', fg = 'blue', command = lambda: self.confirmTD(tdNumber)).grid(row = 3, column = 4)

        self.makeGraphButton = Button(self.master, text = ' Confirm entry', fg = 'blue', command = lambda: self.confirmData(dpNumber)).grid(row = 4, column = 1)

        self.dpHelpButton = Button(self.master, text = 'Help', fg = 'blue', command = lambda : self.helpButton()).grid(row = 4, column = 2)


    def confirmTD(self, tdInput):
            if(tdInput.get() < .00000000002 or tdInput.get() > 10):
                    tkMessageBox.showinfo('Error', 'The time per division must be between 200 picoseconds and 10 seconds')
            else:
                    timeDivision = tdInput.get()
                    td.write('HORIZONTAL:MAIN:SCALE ' + str(timeDivision))
                    print(td.query('HORIZONTAL:MAIN:SCALE?'))

    def confirmData(self, datapoints):
            
            
            
                    td.write('BELL')
                    channel = 1
                    #print channel
                    td.write('Select: 1 ON ')
                    td.write('SELECT:CH2 OFF')
                    td.write('SELECT:CH3 OFF')
                    td.write('SELECT:CH4 OFF')
                    
                    points = datapoints.get()
                    td.write('DATA:SOURCE 1')
                    td.write('DATa:ENCdg ASCII')
                    td.write('MEASUREMENT:IMMED:TYPE PERIOD')
                    divisor = td.query_ascii_values('MEASUREMENT:IMMED:VALUE?')[0]
            
                    td.write('Horizontal:recordlength ' + points)
                    #print(td.query('HORIZONTAL:RECORDLENGTH?'))
                    td.write('DATA:TARGET 1 ' )
                    td.write('DATA:WIDTH 2')
                    td.write('DATA:START 1')
                    td.write('DATA:STOP ' + points)
                    sleep(3)
                    #print'sleep'
                    td.write('*WAI')
                    td.write('WFMPRE:PT_OFF 0')
                    data = []
                    td.query('CH1?')
                    td.write('WFMPRe?')
                    td.write('*WAI')
                    td.write('DATa?')
                    td.query_ascii_values('CURVE?')

        
                    data = td.query_ascii_values('CURVe?')
                    td.write('*WAI')   
                    xAxis =[]
                    counter = 0
                    step =divisor / 500
                    print len(data)
                    for i in range(len(data)):
                    #counter = counter + step
                    #xAxis.append(counter)
                           xAxis.append(i)
                    with open('Oscilloscope.txt', 'w'):pass
                    oFile = open('Oscilloscope.txt', 'a')
                    for i in range(len(data)):
                            oFile.write('The data at point ' + str(xAxis[i]) + ' is ' + str(data[i])+ '\n')
                    oFile.close()

                    plt.plot(xAxis, data)
                    plt.xlabel('Point')
                    plt.ylabel('Data')
                    plt.show()
    def helpButton(self):
            tkMessageBox.showinfo('Help Window',  "When using the oscilloscope, it will read the data in channel one \n \n When Getting the amount of data points, you are limited to the following numbers : 500, 1000, 2500, 5000, 15000, 50000. \n \n The larger the number you pick, the longer it will take to query the information. The interface will show a graph of all the data points present on the screen of the oscilloscope")

    def quitTD(self):
        self.master.destroy()
            

class KEITH():
    def __init__(self,master):
        self.master = master
        self.master.geometry('800x800+150+150')
        self.master.title('Keithly Window')
        self.button1 = Button(self.master, text = 'Quit', fg = 'blue', command = self.quitKeithley).grid(row  = 22, column = 1)
        ke.write(':TRIGger:SEQuence2:TOUT 0')
        self.vscmLabel = Label(self.master, text = 'This will sweep voltage and measure current').grid(row = 1, column = 1)
        
        self.startVoltageLabel = Label(self.master, text = 'Starting voltage: ').grid(row = 2, column = 1)
        startVolt = DoubleVar()
        self.startVoltageEntry = Entry(self.master, textvariable = startVolt).grid(row = 2, column = 2)
        self.svLabel= Label(self.master, text = 'volts').grid(row =2, column = 3)

        self.endVoltageLabel = Label(self.master, text = 'Ending voltage: ').grid(row = 4, column = 1)
        endVolt = DoubleVar()
        self.endVoltageEntry = Entry(self.master, textvariable = endVolt).grid(row = 4, column = 2)
        self.evLabel = Label(self.master, text = 'volts').grid(row = 4, column = 3)

        self.voltStepLabel = Label(self.master, text = 'Voltage step: ').grid(row = 6, column = 1)
        stepVolt = DoubleVar()
        self.stepVoltageEntry = Entry(self.master, textvariable = stepVolt).grid(row = 6, column = 2)
        self.stepLabel = Label(self.master, text = 'volts').grid(row = 6, column = 3)

        self.currentComplianceLabel = Label(self.master, text = 'Current compliance : ').grid(row = 8, column = 1)
        currentCompliance = DoubleVar()
        self.currentComplianceEntry = Entry(self.master, textvariable = currentCompliance).grid(row = 8, column = 2)
        self.ccLabel = Label(self.master, text = 'amps').grid(row = 8, column = 3)

        self.vscmButton = Button(self.master, text = 'Confirm Sweep', fg = 'blue', command = lambda : self.vscmSweep(startVolt, endVolt, stepVolt, currentCompliance)).grid(row = 10, column = 1)

        self.csvmLabel = Label(self.master, text = 'This will sweep current and measure voltage').grid(row = 12, column = 1)
        
        self.startCurrentLabel = Label(self.master, text = 'Starting current: ').grid(row = 14, column = 1)
        startCurrent = DoubleVar()
        self.startCurrentEntry = Entry(self.master, textvariable = startCurrent).grid(row = 14, column = 2)
        self.scLabel = Label(self.master, text = 'amps').grid(row = 14, column = 3)

        self.endCurrentLabel = Label(self.master, text = 'Ending current: ').grid(row = 16, column = 1)
        endCurrent = DoubleVar()
        self.endCurrentyEntry = Entry(self.master, textvariable = endCurrent).grid(row = 16, column = 2)
        self.ecLabel = Label(self.master, text = 'amps').grid(row=16, column = 3)

        self.currentStepLabel = Label(self.master, text = 'Current step: ').grid(row = 18, column = 1)
        stepCurrent = DoubleVar()
        self.stepCurrentEntry = Entry(self.master, textvariable = stepCurrent).grid(row = 18, column = 2)
        self.scLabel = Label(self.master, text = 'amps').grid(row = 18, column= 3)

        self.voltageComplianceLabel = Label(self.master, text = 'Voltage compliance : ').grid(row = 20, column = 1)
        voltageCompliance = DoubleVar()
        self.voltageComplianceEntry = Entry(self.master, textvariable = voltageCompliance).grid(row = 20, column = 2)
        self.vcLabel = Label(self.master, text = 'volts').grid(row = 20, column = 3)

        self.csvmButton = Button(self.master, text = 'Confirm Sweep', fg = 'blue', command = lambda : self.csvmSweep(startCurrent, endCurrent, stepCurrent, voltageCompliance)).grid(row = 22, column = 1)


        self.helpButton = Button(self.master, text = 'Help', fg = 'blue', command = lambda : self.helpOption()).grid(row = 22, column = 2)
        
    def helpOption(self):
            tkMessageBox.showinfo("Help", "Welcome to the Keithly Help Window \n \n This device can sweep voltage and measure current as well as sweep current and measure voltage. \n \n The voltage / current compliance is the maximum voltage/current that the source can supply to the load. \n \n When sweeping voltage and measuring current, the voltage can range from 200 microvolts to 210 volts.  The current compliance must be between -1.05 and 1.05 amps. \n \n When sweeping current and measuring voltage, the current must be between 1 nanoamp and 1.05 amps.  The voltage compliance must stay between -.21 and .21 volts.  \n \n After the sweep is done, the information will be written to either of two text files : VoltageSweepCurrentMeasure.txt or CurrentSweepVoltageMeasure.txt. ")  

        
    def vscmSweep(self, s, e, stepVolt, currentCompliance):
            #print(ke.query(':TRIGger:SEQuence2:TOUT?'))
            ke.timeout = None
            print s.get()
            if(s.get()  < .0002 or s.get() > 210):
                     tkMessageBox.showinfo("Error", "The voltage must be between 200 microvolts and 210 volts")
            else:
                    start = s.get()
            if(e.get()  < .0002 or e.get()> 210):
                    tkMessageBox.showinfo("Error", "The voltage must be between 200 microvolts and 210 volts")
            else:
                    end = e.get()
            step = stepVolt.get()
            voltageLevel = []
            temp = start
            currentLevel = []
            temp2 = 1
            data = 0
            
            if(currentCompliance.get() < -1.05 or currentCompliance.get() > 1.05):
                    tkMessageBox.showinfo("Error", "The compliance must be between -1.05 and 1.05 amps")
            else:
                    compliance = currentCompliance.get()
            numberOfMeasurements = (end-start) / step
            tkMessageBox.showinfo("Warning", "Please click OK to start the sweep, during this time you will not be able to press any other buttons on the interface")
            ke.write('*RST')
            ke.write('*RST')
            ke.write(':SENS:FUNC:CONC OFF')
            ke.write(':SOUR:FUNC VOLT')
            ke.write(':SENSE:FUNC "CURR:DC"')
            ke.write(':SENS:CURR:PROT ' + str(compliance))
            ke.write(':SOUR:VOLT:START ' + str(start))
            ke.write(':SOUR:VOLT:STOP ' + str(end))
            ke.write(':SOUR:VOLT:STEP '+ str(step))
            ke.write(':SOUR:VOLT:MODE SWE')
            ke.write(':SOUR:SWE:RANG AUTO')
            ke.write(':SOUR:SWE:SPAC LIN')
            ke.write(':TRIG:COUN ' + str(numberOfMeasurements+1))
            ke.write(':SOUR:DEL 0.1')
            ke.write('OUTP ON')
            data = ke.query_ascii_values('READ?')
            with open('VoltageSweepCurrentMeasure.txt', 'w'): pass
            vscmFile = open('VoltageSweepCurrentMeasure.txt', 'a')
            vscmFile.write('Voltage sweep performed with current measurements \n')
            vscmFile.write('Starting voltage: ' + str(start) + '\n')
            vscmFile.write('Ending voltage: ' + str(end)+ '\n')
            vscmFile.write('Voltage step: ' + str(step)+ '\n')
            vscmFile.write('Current Compliance: ' + str(compliance)+ '\n')
            del data[0]
            for i in range(int(numberOfMeasurements)+2):
                    voltageLevel.append(start)
                    start = start + step
            i = 0
            for i in range(len(data)):
                    if(i==0):
                        currentLevel.append(data[i])
                    if( i % 5 == 0):
                        currentLevel.append(data[i])
            del currentLevel[0]
            del voltageLevel[-1]
            for k in range(len(voltageLevel)):
                    vscmFile.write('The current at: ' + str(voltageLevel[k]) + ' volts is: ' + str(currentLevel[k]) + ' amps' + '\n')
            print voltageLevel
            print currentLevel
            vscmFile.close()
            plt.grid(True)
            plt.plot(voltageLevel, currentLevel)
            plt.xlabel('Voltage (V)')
            plt.ylabel('Current (A)')
            plt.show()
            self.maxLabel = Label(self.master, text = '').grid(row = 22, column = 3)        

    def csvmSweep(self, startCurrent, endCurrent, stepCurrent, voltageCompliance):
        ke.timeout = None
        if(startCurrent.get() < .000000001 or startCurrent.get() > 1.05):
                tkMessageBox.showinfo('Error', 'The current must be between 1 nanoamp and 1.05 amps')
        else:
                start = startCurrent.get()
        if(endCurrent.get() < .000000001 or endCurrent.get() > 1.05):
                tkMessageBox.showinfo('Error', 'The current must be between 1 nanoamp and 1.05 amps')
        else:
                end = endCurrent.get()
        step = stepCurrent.get()
        voltageLevel = []
        currentLevel = []
        data = 0
        compliance = 0  
        
        if(voltageCompliance.get() > .21 or voltageCompliance.get() < -.21):
                tkMessageBox.showinfo("Error", "The voltage compliance must fall between -.21 and .21 volts")
        else:
                compliance = voltageCompliance.get()
        
        numberOfMeasurements = (end-start) / step 
        tkMessageBox.showinfo("Warning", "Please click OK to start the sweep, during this time you will not be able to press any other buttons on the interface")
        ke.write('*RST')
        ke.write('*RST')
        ke.write(':SENS:FUNC:CONC OFF')
        ke.write(':SOUR:FUNC CURR')
        ke.write(':SENSE:FUNC "VOLT:DC"')
        ke.write(':SENS:VOLT:PROT 1')
        ke.write(':SOUR:CURR:START ' + str(start))
        ke.write(':SOUR:CURR:STOP ' + str(end))
        ke.write(':SOUR:CURR:STEP '+ str(step))
        ke.write(':SOUR:CURR:MODE SWE')
        ke.write(':SOUR:SWE:RANG AUTO')
        ke.write(':SOUR:SWE:SPAC LIN')
        ke.write(':TRIG:COUN ' + str(numberOfMeasurements+1))
        ke.write(':SOUR:DEL 0.1')
        ke.write('OUTP ON')
        data = ke.query_ascii_values('READ?')
        with open('CurrentSweepVoltageMeasure.txt', 'w'): pass
        vscmFile = open('CurrentSweepVoltageMeasure.txt', 'a')
        vscmFile.write('Current sweep performed with voltage measurements \n')
        vscmFile.write('Starting current: ' + str(start) + '\n')
        vscmFile.write('Ending current: ' + str(end)+ '\n')
        vscmFile.write('Current step: ' + str(step)+ '\n')
        vscmFile.write('Voltage Compliance: ' + str(compliance)+ '\n')
        for i in range(int(numberOfMeasurements)+1):
            currentLevel.append(start)
            start = start + step            
        for i in range(len(data)):
            if(i==0):
                voltageLevel.append(data[i])
            if( i % 5 == 0):
                voltageLevel.append(data[i])
           
        del voltageLevel[0]        

        for k in range(len(currentLevel)):
            vscmFile.write('The voltage at: ' + str(currentLevel[k]) + ' amps is: ' + str(voltageLevel[k]) + ' volts' + '\n')
        print('voltage level: ' + str(voltageLevel))
        print('current level: ' + str(currentLevel))
        vscmFile.close()
        plt.grid(True)
        plt.plot(currentLevel, voltageLevel)
        plt.xlabel('Current (A)')
        plt.ylabel('Voltage (V)')
        
        plt.show()
        

    def quitKeithley(self):
        self.master.destroy()
                              
#class and functions for the AQ4321A laser tuner
class AQA():
    def __init__(self,master):
        #displays the master window.
        self.master = master
        self.master.geometry('1250x800+150+50')
        self.master.title('AQA4321A Window')
        self.button1 = Button(self.master, text = "QUIT", fg = 'blue',command = self.quitAQA).grid(row=10,column=20)
        self.helpButton = Button(self.master, text = 'Help', fg = 'blue', command = self.showHelp).grid(row = 10, column = 21)
        #gives user the option to set the wavelength of the device in nm
        self.waveLength = Label(self.master,  text = 'Please enter the desired parameter').grid(row=6, column = 1)
        v = DoubleVar()
        self.wlEntryBox = Entry(self.master, textvariable = v).grid(row=6, column =2)
        self.waveLengthLabel = Label(self.master, text = "nM").grid(row = 6, column = 3)
        self.button2 = Button(self.master, text = "Confirm ", fg = 'blue', command = lambda: self.validateWV(v)).grid(row = 6, column = 4)

        #gives user the option to set the power level in either dBm or mW, must type out units correctly
        self.powerLevel = Label(self.master, text = 'Please enter the desired power level').grid(row = 8, column = 1)
        power_in = DoubleVar()
        self.userPL = Entry(self.master, textvariable = power_in).grid(row = 8, column = 2)
        units_in = StringVar()
        self.unitsEntryBox = Entry(self.master, textvariable = units_in).grid(row=8,column = 3)
        self.pwr_button = Button(self.master, text = "Confirm Power", fg = 'blue', command = lambda: self.validatePW(power_in,units_in)).grid(row = 8, column = 4)
        self.unitsLabel = Label(self.master, text = "Units must be dBm or mW").grid(row=8, column=5)

        #gives user the option to set the frequency of the device
        self.freqLevel = Label(self.master, text = 'Please enter the desired frequency').grid(row = 10, column = 1)
        freqIn = DoubleVar()
        self.freqEntryBox = Entry(self.master, textvariable = freqIn).grid(row = 10, column = 2)
        self.freqLabel = Label(self.master, text = "THz").grid(row=10, column = 3)
        self.confirmFreq = Button (self.master, text = "Confirm frequency", fg = 'blue', command = lambda : self.validateFreq(freqIn)).grid(row = 10, column =4)

        #displays the power level in dBm and mW, frequency, and wavelength on screen.
        self.getInformation = Button(self.master, text = "Get information", fg = 'blue', command = lambda : self.getData()).grid(row = 12, column =5)



        self.lowerSweepLabel = Label(self.master, text = 'Please enter the starting bound for the sweep: ').grid(row = 18, column = 1)
        lowerSweep = DoubleVar()
        self.lowerSweepBox = Entry(self.master, textvariable = lowerSweep).grid(row=18, column = 2)
        self.lowerSweepUnitsLabel = Label(self.master, text = 'nanometers').grid(row=18,column =3)
       


        self.upperSweepLabel = Label(self.master, text = 'Please enter the ending bound for the sweep: ').grid(row = 20, column = 1)
        upperSweep = DoubleVar()
        self.upperSweepBox = Entry(self.master, textvariable = upperSweep).grid(row = 20, column = 2)
        self.upperSweepUnitsLabel = Label(self.master, text = 'nanometers').grid(row=20,column =3)
       

        self.sweepStepLabel = Label(self.master, text = 'Please enter the sweep step in nanometers: ').grid(row = 22, column = 1)
        sweepStep = DoubleVar()
        self.sweepStepBox = Entry(self.master, textvariable = sweepStep).grid(row = 22, column = 2)
        self.helpLabel = Label(self.master, text = 'Entering a number will trigger step mode, entering a zero will enter continous mode').grid(row=22,column = 3)

        self.ssTimeLabel = Label(self.master, text = 'Please enter the sweep step time in seconds: ').grid(row = 24, column = 1)
        ssTime = DoubleVar()
        self.ssEntry = Entry(self.master, textvariable = ssTime).grid(row = 24, column = 2)
        self.help1Label = Label(self.master, text ='Please leave as 0 if you intend on using continuous mode').grid(row = 24, column = 3)

        self.sTimeLabel = Label(self.master, text = 'Please enter the continuous time sweep length in seconds: ').grid(row = 26, column = 1)
        sTime = DoubleVar()
        self.sEntry = Entry(self.master, textvariable = sTime).grid(row = 26, column = 2)
        self.help2Label = Label(self.master, text = 'Please leave as 0 if you intend on using step mode').grid(row = 26, column = 3)

        self.confirmSweep = Button(self.master, text = 'Confirm sweep', fg = 'blue', command = lambda: self.runNanometerSweep(lowerSweep, upperSweep, sweepStep, ssTime, sTime)).grid(row = 28, column = 1)        


        self.startPowerLevelLabel = Label(self.master, text = 'Please enter the starting power level: ').grid(row = 34, column = 1)
        startPower = DoubleVar()
        self.startPowerEntry = Entry(self.master, textvariable = startPower).grid(row = 34, column = 2)
        powerSweepUnits = StringVar()
        self.powerSweepUnitsEntry = Entry(self.master, textvariable = powerSweepUnits).grid(row = 34, column = 3)
        self.powerSweepUnitsLabel = Label(self.master, text = 'Please enter the units in either dBm or mW').grid(row = 34, column = 4)

        self.endPowerLevelLabel = Label(self.master, text = 'Please enter the ending power level: ').grid(row = 36, column = 1)
        endPower = DoubleVar()
        self.endPowerEntry = Entry(self.master, textvariable = endPower).grid(row = 36, column = 2)

        self.powerStepLabel = Label(self.master, text = 'Please enter the step amount for the power: ').grid(row = 38, column = 1)
        powerStep = DoubleVar()
        self.powerStepEntry = Entry(self.master, textvariable = powerStep).grid(row = 38, column = 2)

        self.powerTimeLabel = Label(self.master, text = 'Please enter the time between each step in seconds: ').grid(row = 40, column = 1)
        powerTime = DoubleVar()
        self.powerTimeEntry = Entry(self.master, textvariable = powerTime).grid(row = 40, column = 2)

        self.powerSweepButton = Button(self.master, text = 'Run power sweep', fg = 'blue', command = lambda : self.runPowerSweep(startPower, endPower, powerSweepUnits, powerStep, powerTime)).grid(row = 42, column = 1)


        self.meterLabel = Label(self.master, text = 'Please specify the units for the meter as dBm or mW').grid(row = 44, column=1)
        opmrUnits = StringVar()
        self.meterEntry = Entry(self.master, textvariable = opmrUnits).grid(row = 44, column = 2)
        self.meterOnButton = Button(self.master, text = 'Turn on 1830-R Power Meter', fg='blue', command = lambda: self.turnOn1830R(opmrUnits)).grid(row = 46, column = 1)
        self.meterOffButton = Button(self.master, text = 'Turn Off 1830-R Power Meter', fg = 'blue', command = lambda: self.turnOff1830R()).grid(row = 46, column = 2)
        

    def turnOn1830R(self, opmrUnits):
        global opmrOn, opmr
        if('GPIB0::4::INSTR' in rm.list_resources()):
                opmrOn = True
                opmr = rm.open_resource('GPIB0::4::INSTR')
        if(opmrOn == True):
                units = opmrUnits.get()
                if(units == 'mW'):
                    opmr.write('U1')
                elif(units == 'dBm'):
                    opmr.write('U3')
                else:
                    tkMessageBox.showinfo("Error", "Please enter the correct units")
                    
        if(opmrOn != True):
                tkMessageBox.showinfo('Error', 'Please make sure that the optical power meter is plugged in')

    def turnOff1830R(self):
        global opmrOn
        if(opmrOn == True):
                opmrOn = False
    #validate functions make sure that the input from the user is in the correct bounds for the device, else it will show an error message giving the correct bounds.
    def validateWV(self, wavelength_in):
        aq.write('TSTEPU0')    
        s = wavelength_in.get()
        if(s < 1480 or s > 1580):
                tkMessageBox.showinfo("Error", "The wavelength you entered was incorrect, please keep the value between 1480.000 and 1580.000 nM")

        else:
                aq.write("TWL " + '%.3f' % s)


    def showHelp(self):
            tkMessageBox.showinfo("Helpful Information", "Welcome to the AQ4321A Window \n \n The wavelength must be between 1480 and 1580 nM \n \n When using the power level, you must specift the units as either dBm or mW \n \n If using dBm, you must be between -20 and 8 dBm, while for mW you have to be between .01 and 6.31 mW \n \n The starting and ending bounds for the sweep are both in nanometers and must fall between 1480 and 1580 nM \n \n  When using the step mode, please specify a step amount in nM between .001 and 100 as well as a time between each step in seconds from .01 to 999 seconds \n \n When using continuous time, leave the sweep step and sweep step time as 0, the continuous time is how long it takes to step through the range and must be between 1 and 99999 seconds\n \n You can also do a stepping sweep with power, you must specify the power as either mW or dBm, all the other parameters are the same.")


    def validatePW(self, power_in,units_in):
        pIn = power_in.get()
        uIn = units_in.get()

        if(uIn == "dBm"):

                if(pIn < -20 or pIn > 8):
                        tkMessageBox.showinfo("Error", "The power level must be between -20 dBm and 10 dBM")
                else:
                        aq.write("TPDB " + '%.1f' % pIn)
        if(uIn == "mW"):
                if(pIn < .010 or pIn > 6.31):
                        tkMessageBox.showinfo("Error", "The power level must be between .01 mW and 10 mW")
                else:
                        aq.write("TPMW " + '%.3f' % pIn)

        if(uIn != "mW" and uIn != "dBm"):
                tkMessageBox.showinfo("Error", "The units must be in dBm or mW")

    def validateFreq(self, freqIn):
            fIn = freqIn.get()
            aq.write('TSTEPU1')

            if(fIn <189.7421 or fIn > 202.5625):
                    tkMessageBox.showinfo("Error", "The frequency must be between 189.7421 THz and 202.5625 THz")
            else:
                    aq.write("TFR " + '%.4f' % fIn)

    #this function gets the different parameters directly from the device.
    def getData(self):
            dbm = float(aq.query("TPDB?"))
            mw = float(aq.query("TPMW?"))
            wl = float(aq.query("TWL?"))
            freq = float(aq.query("TFR?"))

            dbmLabel = Label(self.master, text = "The measured power is " + ' %.3f ' % dbm + "dBm", fg = 'red').grid(row=12, column = 1)
            mwLabel = Label(self.master, text = "The measured power is" + ' %.3f ' % mw + "mW", fg = 'red').grid(row=12, column =3)
            wlLabel = Label(self.master, text = "The measured wavelength is" + ' %.3f ' % wl + "nM", fg = 'red').grid(row=14, column = 1)
            freqLabel = Label(self.master, text = "The measured frequency is" + ' %.3f ' % freq + "THz", fg = 'red').grid(row=14, column =3)


    def runNanometerSweep(self, first, second, stepAmount, ssTime, sTime):
            start = first.get()
            end = second.get()
            step = stepAmount.get()
            stepTime = ssTime.get()
            contTime = sTime.get()
            stepFlag = False
            aq.write('TW ' + '%.3f' % start)
            aq.write('L1')
            aq.write('TSTP')
            
            
            print(stepTime)
            print(contTime)
            print(start)
            print(end)
            if (step > 0):
                    negativeFlag = False
            if(step < 0):
                    negativeFlag = True
            if(step == 0):
                    negativeFlag = False
                    

            if(negativeFlag ==True):          
                    if( (start > end) and step < 0):
                            
                            difference = end - start
                            stepRange = int(difference / step)
                            for i in range(stepRange + 1):
                                    aq.write("TWL " + '%.3f' % start)
                                    start = start + step
                                    sleep(stepTime)
                            aq.write('TSTP')

                            
            if(negativeFlag == False):

                    if(stepTime == 0 and contTime != 0):
                            stepFlag = False
                    if(stepTime != 0 and contTime ==0):
                            stepFlag = True
                    

                    if(stepFlag == False):
                            if(contTime < 1.0 or contTime > 99999):
                                    tkMessageBox.showinfo("Error", "The time must be between 1 and 99999 seconds")
                            else:
                                    aq.write('TSWET ' + '%.2f' % contTime)
                    if(stepFlag == True):
                            if(stepTime < .01 or stepTime > 999):
                                    tkMessageBox.showinfo("Error", "The time must be between 0.1 and 999.0 seconds")
                            else:
                                    aq.write('TSTET ' + '%.2f' % stepTime)
                    
                    if((end > start) and step >= 0):
                            


                            if(start < 1480.000 or start > 1580.000):
                                    tkMessageBox.showinfo("Error", "The lower bound must be between 1520.000 and 1620.000 nM")

                            else:
                                    aq.write('TSTAWL ' + '%.3f' % start)
                                    aq.write('WAIT0.1')

                            if(end < 1480.000 or end > 1580.000):
                                    tkMessageBox.showinfo("Error", "The upper bound must be between 1480.000 and 1580.000 nM")

                            else:
                                    aq.write('TSTPWL ' + '%.3f' % end)
                                    aq.write('WAIT0.1')
                            
                            if((step < 0.001 and step!= 0) or step > 100.000):
                                    tkMessageBox.showinfo("Error", "The step must be between 0.0001 and 100.000.  Enter '0' for continuous sweep.")
                            

                            if(stepFlag == False):
                            
                                    aq.write('TSWM1')
                                    aq.write('TSWEL0')
                                    aq.write('TSGL')

                                    
                                    
                                    
                            else:
                                    
                                    aq.write('TSWM0')
                                    aq.write("TSTEWL " + '%.4f' % step)
                                    aq.write('WAIT0.1')
                                    
                                    aq.write('TSGL')

                   
                                    

                   

    def runPowerSweep(self, startPow, endPow, unitsPow, powStep, powTime):
            global opmr
            start =initial =  startPow.get()
            end = ending = endPow.get()
            units = unitsPow.get()
            step = powStep.get()
            difference = end - start
            actualStep = int(difference / step)
            print start
            print end
            print step
            powerActual = []
            powerMeasured = []
        
            if((start > end) and (step > 0)):
                    tkMessageBox.showinfo("Error", "You cannot have a starting value larger than the ending with a positive step, please try again.")
            if((end > start) and (step < 0)):
                    tkMessageBox.showinfo("Error", "You cannot have an ending value larger than the starting with a negative step, please try again.")

        
            if(powTime.get() == None):
                    time = .1
            else:
                    time = powTime.get()
           
            if(units == 'dBm'):
                aq.write('TPOU0')
                if(start < -20 or start > 8):
                        tkMessageBox.showinfo("Error", "The starting power level must be between -20 and 8 dBm")
                        
                if(end < -20 or end > 8):
                        tkMessageBox.showinfo("Error", "The ending power level must be between -20 and 8 dBm")
                aq.write('TPDB ' + '%.1f' % start)
                sleep(2)       
                while(end >= start):
                        aq.write("TPDB " + '%.1f' % start)
                        powerActual.append(start)
                        measurement = opmr.query_ascii_values('D?')
                        print measurement
                        sleep(.5)
                        powerMeasured.append(measurement[0])
                        start = start + step                                                      
                        sleep(time)
                del powerMeasured[0]
                powerMeasured.append(opmr.query_ascii_values('D?')[0])
                print powerActual
                print powerMeasured
                plt.plot(powerActual, powerMeasured)
                plt.xlabel('Actual Power in dBm')
                plt.ylabel('Measured Power in dBm')
                with open('AQA DBM Sweep.txt', 'w'):pass
                aqdbmFile = open('AQA DBM Sweep.txt', 'a')
                aqdbmFile.write('Start sweep: ' + str(initial)+ '\n')
                aqdbmFile.write('End sweep: ' + str(ending)+ '\n')
                aqdbmFile.write('Sweep step: ' + str(step) + '\n')
                aqdbmFile.write('Power units: dBm' + '\n')

                for i in range(len(powerActual)):
                        aqdbmFile.write(str(powerActual[i]) + ' ' + str(powerMeasured[i]) + '\n')
                aqdbmFile.close()
                plt.show()

            if(units == 'mW'):
                aq.write('TPOU1')
                   
                if(start < .010 or start > 6.31):
                        tkMessageBox.showinfo("Error", "The starting power level must be between .01 and 6.31 mW")
                           
                if(end < .010 or end > 6.31):
                        tkMessageBox.showinfo("Error", "The ending power level mus tbe between .01 and 6.31 mW")
                aq.write('TPDB ' + '%.1f' % start)
                sleep(2)           
                while(end >= start):
                        aq.write("TPMW " + '%.4f' % start)
                        powerActual.append(start)
                        measurement = opmr.query_ascii_values('D?')
                        sleep(.5)
                        powerMeasured.append(measurement[0])
                        start = start + step
                        sleep(time)
                del powerMeasured[0]
                powerMeasured.append(opmr.query_ascii_values('D?')[0])
                print powerActual
                print powerMeasured
                plt.plot(powerActual, powerMeasured)
                plt.xlabel('Actual Power in mW')
                plt.ylabel('Measured Power in mW')
                with open('AQA MW Sweep.txt', 'w'):pass
                aqdbmFile = open('AQA MW Sweep.txt', 'a')
                aqdbmFile.write('Start sweep: ' + str(initial)+ '\n')
                aqdbmFile.write('End sweep: ' + str(ending)+ '\n')
                aqdbmFile.write('Sweep step: ' + str(step) + '\n')
                aqdbmFile.write('Power units: mW' + '\n')

                for i in range(len(powerActual)):
                        aqdbmFile.write(str(powerActual[i]) + ' ' + str(powerMeasured[i]) + '\n')
                aqdbmFile.close()
                plt.show()
                           
            if(units != 'mW' and units != 'dBm'):
                   tkMessageBox.showinfo("Error", "Please enter the correct units, either dBm or mW")
                           

    #closes the window
    def quitAQA(self):

        self.master.destroy()

class AQD:
    def __init__(self,master):
        #displays the master window.
        self.master = master
        self.master.geometry('1300x800+150+50')
        self.master.title('AQA4321D Window')
        self.button1 = Button(self.master, text = "QUIT", fg = 'blue',command = self.quitAQD).grid(row=6,column=20)

        #gives user the option to set the wavelength of the device in nm
        self.waveLength = Label(self.master, text = 'Please enter the desired wavelength', fg = 'red').grid(row = 6, column =1)
        v = DoubleVar()
        self.wlEntryBox = Entry(self.master, textvariable = v).grid(row = 6, column = 2)
        self.confirmWavelength = Button(self.master, text = "Confirm Wavelength", fg = 'blue', command = lambda: self.validateWV(v)).grid(row=6, column =3)

        #gives user the option to set the power level in either dBm or mW, must type out units correctly
        self.powerLevel = Label(self.master, text = 'Please enter the desired power level', fg = 'red').grid(row = 8, column = 1)
        power_in = DoubleVar()
        self.userPL = Entry(self.master, textvariable = power_in).grid(row =8, column = 2)
        units_in = StringVar()
        self.unitsEntryBox = Entry(self.master, textvariable = units_in).grid(row = 8, column = 3)
        self.pwr_button = Button(self.master, text = "Confirm Power", fg = 'blue', command = lambda:self.validatePW(power_in,units_in)).grid(row=8,column = 4)
        self.unitsLabel = Label(self.master, text = "Units must be dBm or mW", fg = 'red').grid(row = 8, column = 5)

        #gives user the option to set the frequency of the device
        self.freqLevel = Label(self.master, text = 'Please enter the desired frequency', fg = 'red').grid(row = 10, column = 1)
        freqIn = DoubleVar()
        self.freqEntryBox = Entry(self.master, textvariable = freqIn).grid(row = 10, column = 2)
        self.freqLabel = Label(self.master, text = "THz", fg = 'red').grid(row=10, column = 3)
        self.confirmFreq = Button (self.master, text = "Confirm frequency", fg = 'blue', command = lambda : self.validateFreq(freqIn)).grid(row = 10, column =4)


        #displays the power level in dBm and mW, frequency, and wavelength on screen.
        self.getInformation = Button(self.master, text = "Get information", fg = 'blue', command = lambda : self.getData()).grid(row = 12, column =5)


        self.lowerSweepLabel = Label(self.master, text = 'Please enter the starting bound for the sweep: ').grid(row = 18, column = 1)
        lowerSweep = DoubleVar()
        self.lowerSweepBox = Entry(self.master, textvariable = lowerSweep).grid(row=18, column = 2)
        self.lowerSweepUnitsLabel = Label(self.master, text = 'nanometers').grid(row=18,column =3)
       


        self.upperSweepLabel = Label(self.master, text = 'Please enter the ending bound for the sweep: ').grid(row = 20, column = 1)
        upperSweep = DoubleVar()
        self.upperSweepBox = Entry(self.master, textvariable = upperSweep).grid(row = 20, column = 2)
        self.upperSweepUnitsLabel = Label(self.master, text = 'nanometers').grid(row=20,column =3)
       

        self.sweepStepLabel = Label(self.master, text = 'Please enter the sweep step in nanometers: ').grid(row = 22, column = 1)
        sweepStep = DoubleVar()
        self.sweepStepBox = Entry(self.master, textvariable = sweepStep).grid(row = 22, column = 2)
        self.helpLabel = Label(self.master, text = 'Entering a number will trigger step mode, entering a zero will enter continous mode').grid(row=22,column = 3)

        self.ssTimeLabel = Label(self.master, text = 'Please enter the sweep step time in seconds: ').grid(row = 24, column = 1)
        ssTime = DoubleVar()
        self.ssEntry = Entry(self.master, textvariable = ssTime).grid(row = 24, column = 2)

        self.sTimeLabel = Label(self.master, text = 'Please enter the continuous time sweep length in seconds: ').grid(row = 26, column = 1)
        sTime = DoubleVar()
        self.sEntry = Entry(self.master, textvariable = sTime).grid(row = 26, column = 2)

        self.confirmSweep = Button(self.master, text = 'Confirm sweep', fg = 'blue', command = lambda: self.runNanometerSweep(lowerSweep, upperSweep, sweepStep, ssTime, sTime)).grid(row = 28, column = 1)        


        self.startPowerLevelLabel = Label(self.master, text = 'Please enter the starting power level: ').grid(row = 34, column = 1)
        startPower = DoubleVar()
        self.startPowerEntry = Entry(self.master, textvariable = startPower).grid(row = 34, column = 2)
        powerSweepUnits = StringVar()
        self.powerSweepUnitsEntry = Entry(self.master, textvariable = powerSweepUnits).grid(row = 34, column = 3)
        self.powerSweepUnitsLabel = Label(self.master, text = 'Please enter the units in either dBm or mW').grid(row = 34, column = 4)

        self.endPowerLevelLabel = Label(self.master, text = 'Please enter the ending power level: ').grid(row = 36, column = 1)
        endPower = DoubleVar()
        self.endPowerEntry = Entry(self.master, textvariable = endPower).grid(row = 36, column = 2)

        self.powerStepLabel = Label(self.master, text = 'Please enter the step amount for the power: ').grid(row = 38, column = 1)
        powerStep = DoubleVar()
        self.powerStepEntry = Entry(self.master, textvariable = powerStep).grid(row = 38, column = 2)

        self.powerTimeLabel = Label(self.master, text = 'Please enter the time between each step in seconds: ').grid(row = 40, column = 1)
        powerTime = DoubleVar()
        self.powerTimeEntry = Entry(self.master, textvariable = powerTime).grid(row = 40, column = 2)

        self.powerSweepButton = Button(self.master, text = 'Run power sweep', fg = 'blue', command = lambda : self.runPowerSweep(startPower, endPower, powerSweepUnits, powerStep, powerTime)).grid(row = 42, column = 1)





        

    #validate functions make sure that the input from the user is in the correct bounds for the device, else it will show an error message giving the correct bounds.
    def validateWV(self, wavelength_in,):
        wIn = wavelength_in.get()
        
       
        if(wIn < 1520 or wIn > 1620):
                tkMessageBox.showinfo("Error", "The wavelength you entered was incorrect, please keep the value between 1520.000 and 1620.000 nM")

        else:
                aqd.write("TWL " + '%.3f' % wIn)
    
    def validatePW(self, power_in,units_in):
        pIn = power_in.get()
        uIn = units_in.get()

        if(uIn == "dBm"):

                if(pIn < -20 or pIn > 7):
                        tkMessageBox.showinfo("Error", "The power level must be between -20 dBm and 10 dBM")
                else:
                        aqd.write("TPDB " + '%.1f' % pIn)
        if(uIn == "mW"):
                if(pIn < .010 or pIn > 5.012):
                        tkMessageBox.showinfo("Error", "The power level must be between .01 mW and 10 mW")
                else:
                        aqd.write("TPMW " + '%.3f' % pIn)

        if(uIn != "mW" and uIn != "dBm"):
                tkMessageBox.showinfo("Error", "The units must be in dBm or mW")


    def validateFreq(self, freqIn):
            fIn = freqIn.get()

            if(fIn < 185.0571 or fIn > 197.2319):
                    tkMessageBox.showinfo("Error", "The frequency must be between 185.0571 THz and 197.2139 THz")
            else:
                    aqd.write("TFR " + '%.4f' % fIn)

    #this function gets the different parameters directly from the device.
    def getData(self):
            dbm = float(aqd.query("TPDB?"))
            mw = float(aqd.query("TPMW?"))
            wl = float(aqd.query("TWL?"))
            freq = float(aqd.query("TFR?"))

            dbmLabel = Label(self.master, text = "The measured power is " + ' %.3f ' % dbm + "dBm", fg = 'red').grid(row=14, column = 1)
            mwLabel = Label(self.master, text = "The measured power is" + ' %.3f ' % mw + "mW", fg = 'red').grid(row=14, column =3)
            wlLabel = Label(self.master, text = "The measured wavelength is" + ' %.3f ' % wl + "nM", fg = 'red').grid(row=16, column = 1)
            freqLabel = Label(self.master, text = "The measured frequency is" + ' %.3f ' % freq + "THz", fg = 'red').grid(row=16, column =3)

    def runNanometerSweep(self, first, second, stepAmount, ssTime, sTime):
            start = first.get()
            end = second.get()
            step = stepAmount.get()
            stepTime = ssTime.get()
            contTime = sTime.get()
            stepFlag = False
            aq.write('TW ' + '%.3f' % start)
            aq.write('L1')
            aq.write('TSTP')
            
            if (step > 0):
                    negativeFlag = False
            if(step < 0):
                    negativeFlag = True
            if(step == 0):
                    negativeFlag = False
                    

            if(negativeFlag ==True):          
                    if( (start > end) and step < 0):
                            
                            difference = end - start
                            stepRange = int(difference / step)
                            for i in range(stepRange + 1):
                                    aqd.write("TWL " + '%.3f' % start)
                                    start = start + step
                                    sleep(stepTime)
                            aqd.write('TSTP')

                            
            if(negativeFlag == False):

                    if(stepTime == 0 and contTime != 0):
                            stepFlag = False
                    if(stepTime != 0 and contTime ==0):
                            stepFlag = True
                    

                    if(stepFlag == False):
                            if(contTime < 1.0 or contTime > 99999):
                                    tkMessageBox.showinfo("Error", "The time must be between 1 and 99999 seconds")
                            else:
                                    aqd.write('TSWET ' + '%.2f' % contTime)
                    if(stepFlag == True):
                            if(stepTime < .01 or stepTime > 999):
                                    tkMessageBox.showinfo("Error", "The time must be between 0.1 and 999.0 seconds")
                            else:
                                    aqd.write('TSTET ' + '%.2f' % stepTime)
                    
                    if((end > start) and step >= 0):
                            


                            if(start < 1520.000 or start > 1620.000):
                                    tkMessageBox.showinfo("Error", "The lower bound must be between 1520.000 and 1620.000 nM")

                            else:
                                    aqd.write('TSTAWL ' + '%.3f' % start)
                                    aqd.write('WAIT0.1')

                            if(end < 1520.000 or end > 1620.000):
                                    tkMessageBox.showinfo("Error", "The upper bound must be between 1480.000 and 1580.000 nM")

                            else:
                                    aqd.write('TSTPWL ' + '%.3f' % end)
                                    aqd.write('WAIT0.1')
                            
                            if((step < 0.001 and step!= 0) or step > 100.000):
                                    tkMessageBox.showinfo("Error", "The step must be between 0.0001 and 100.000.  Enter '0' for continuous sweep.")
                            

                            if(stepFlag == False):
                            
                                    aqd.write('TSWM1')
                                    aqd.write('TSWEL0')
                                    aqd.write('TSGL')

                                    
                                    
                                    
                            else:
                                    
                                    aqd.write('TSWM0')
                                    aqd.write("TSTEWL " + '%.4f' % step)
                                    aqd.write('WAIT0.1')
                                    
                                    aqd.write('TSGL')

                   
                                    

                   

    def runPowerSweep(self, startPow, endPow, unitsPow, powStep, powTime):
            start = startPow.get()
            end = endPow.get()
            units = unitsPow.get()
            step = powStep.get()
            difference = end - start
            actualStep = int(difference / step)
            print(start)
            print(end)
            print(units)
            print(step)

        
            if((start > end) and (step > 0)):
                    tkMessageBox.showinfo("Error", "You cannot have a starting value larger than the ending with a positive step, please try again.")
            if((end > start) and (step < 0)):
                    tkMessageBox.showinfo("Error", "You cannot have an ending value larger than the starting with a negative step, please try again.")

        
            if(powTime.get() == None):
                    time = .1
            else:
                    time = powTime.get()
           
            if(units == 'dBm'):
                aqd.write('TPOU0')
                if(start < -20 or start > 7):
                        tkMessageBox.showinfo("Error", "The starting power level must be between -20 and 8 dBm")
                if(end < -20 or end > 7):
                        tkMessageBox.showinfo("Error", "The ending power level must be between -20 and 8 dBm")
                for i in range(actualStep +1):
                        aqd.write("TPDB " + '%.1f' % start)                            
                        start = start + step                                                      
                        sleep(time)
                            
            if(units == 'mW'):
                aqd.write('TPOU1')
                   
                if(start < .010 or start > 5.012):
                        tkMessageBox.showinfo("Error", "The starting power level must be between .01 and 6.31 mW")
                           
                if(end < .010 or end > 5.012):
                        tkMessageBox.showinfo("Error", "The ending power level mus tbe between .01 and 6.31 mW")
                           
                for i in range(actualStep + 1):
                        aqd.write("TPMW " + '%.4f' % start)
                        start = start + step
                        sleep(time)
                           
            if(units != 'mW' and units != 'dBm'):
                   tkMessageBox.showinfo("Error", "Please enter the correct units, either dBm or mW")
                           

    #closes the window
    def quitAQD(self):
        self.master.destroy()


#class to control the optical power meter
class OPM:
    def __init__(self,master):
        self.master = master
        self.master.geometry('900x900+50+50')
        self.master.title('Optical Power Meter Window')
        self.button1 = Button(self.master, text = "QUIT", fg = 'blue',command = self.quitOPM).grid(row=6,column=3)
    def quitOPM(self):
        self.master.destroy()

#class to control the spectrum analyzer
class SA:
    def __init__(self,master):
        self.master = master
        self.master.geometry('900x900+50+50')
        self.master.title('Spectrum Analyzer Window')
        self.button1 = Button(self.master, text = "QUIT", fg = 'blue',command = self.quitSA).grid(row=6,column=3)
    def quitSA(self):
        self.master.destroy()

#class to control the lightwave multimeter
class LM:
    def __init__(self,master):
        self.master = master
        self.master.geometry('900x900+50+50')
        self.master.title('Lightwave Multimeter Window')
        self.button1 = Button(self.master, text = "QUIT", fg = 'blue',command = self.quitLM).grid(row=6,column=3)

        self.powerUnitsLabel = Label(self.master, text = 'Please enter the power level you wish to query as dbm / watt: ').grid(row = 10, column = 1)
        powerUnits = StringVar()
        self.powerUnitsEntry = Entry(self.master, textvariable = powerUnits).grid(row=10, column = 2)
        self.powerUnitsButton = Button(self.master, text = 'Confirm', fg= 'blue', command = lambda: self.confirmPowerUnits(powerUnits)).grid(row = 10, column = 3)

        self.getPowerLevelButton = Button(self.master, text = 'Get Power Level', fg = 'blue', command = lambda:self.getPowerLevel()).grid(row  = 12, column = 1)


        self.powerSourceLevelLabel = Label(self.master, text = 'Please enter the power level : ').grid(row = 14, column = 1)
        self.powerSourceUnitsLabel = Label(self.master, text = 'Please enter units for power : dbm/watt').grid(row = 16, column = 1)
        psl = DoubleVar()
        psu = StringVar()
        self.powerSourceLevelEntry = Entry(self.master, textvariable = psl).grid(row = 14, column = 2)
        self.powerSourceUnitsEntry = Entry(self.master, textvariable = psu).grid(row = 16, column = 2)
        self.powerSourceButton = Button(self.master, text = 'Confirm power level and units', fg = 'blue', command = lambda:self.confirmPowerSourceLevels(psl, psu)).grid(row = 16, column = 3)
        
        self.wavelengthLabel = Label(self.master, text = 'Please enter the wavelength in nm').grid(row = 18, column = 1)
        wl = DoubleVar()
        self.wavelengthEntry = Entry(self.master, textvariable = wl).grid(row = 18, column = 2)
        self.wavelengthButton = Button(self.master, text = 'Confirm', fg = 'blue', command = lambda:self.confirmWL(wl)).grid(row = 18, column = 3)



        self.wlSweepStartLabel= Label(self.master, text = 'Enter starting wavelength').grid(row = 20, column = 1)
        wlStart = DoubleVar()
        self.wlSweepStartEntry = Entry(self.master, textvariable = wlStart).grid(row = 20, column = 2)

        self.wlSweepStartLabel= Label(self.master, text = 'Enter ending wavelength').grid(row = 22, column = 1)
        wlEnd = DoubleVar()
        self.wlSweepEndEntry = Entry(self.master, textvariable = wlEnd).grid(row = 22, column = 2)
        
        self.wlSweepStepLabel = Label(self.master, text = 'Enter sweep step').grid(row = 24, column = 1)
        wlStep = DoubleVar()
        self.wlSweepStepEntry = Entry(self.master, textvariable = wlStep).grid(row = 24, column = 2)
        self.sweepTimeLabel = Label(self.master, text = 'Enter the time between steps in seconds').grid(row = 26, column= 1)
        wlTime= DoubleVar()
        self.sweepTimeEntry = Entry(self.master, textvariable = wlTime).grid(row = 26, column = 2)
        self.confirmSweepButton = Button(self.master, text = 'Confirm sweep', fg = 'blue', command = lambda:self.confirmSweep(wlStart, wlEnd, wlStep, wlTime)).grid(row = 26, column = 3)

        self.syncWavelengthLabel = Label(self.master, text = 'Enter wavelength for power sensor and tunable laser in nm').grid(row = 28, column = 1)
        syncWl = DoubleVar()
        self.syncWaveLengthEntry = Entry(self.master, textvariable = syncWl).grid(row = 28, column = 2)
        self.syncWaveLengthButton = Button(self.master, text = 'Confirm wavelength', fg = 'blue', command = lambda: self.syncwl(syncWl)).grid(row = 28, column = 3)

        self.laserOnLabel = Label(self.master, text = 'Please enter on or off to control laser output').grid(row = 8, column= 1)
        laserOn = StringVar()
        self.laserOnEntry = Entry(self.master, textvariable = laserOn).grid(row = 8, column = 2)
        self.laserOnButton = Button(self.master, text = 'Confirm', fg ='blue', command= lambda: self.controlLaser(laserOn)).grid(row = 8, column = 3)

        self.powerStepStartLabel = Label(self.master, text = 'Please enter starting power level: ').grid(row = 30, column = 1)
        powerStart = DoubleVar()
        self.powerStepStartEntry = Entry(self.master, textvariable = powerStart).grid(row = 30, column = 2)

        self.powerStepEndLabel = Label(self.master, text = 'Please enter ending power level: ').grid(row = 32, column = 1)
        powerEnd = DoubleVar()
        self.powerStepEndEntry = Entry(self.master, textvariable = powerEnd).grid(row = 32, column = 2)

        self.powerStepStepLabel = Label(self.master, text = 'Please enter the power step: ').grid(row = 34, column = 1)
        powerStep = DoubleVar()
        self.powerStepStepEntry = Entry(self.master, textvariable = powerStep).grid(row = 34, column = 2)

        self.powerStepUnitsLabel = Label(self.master, text = 'Please enter dbm/watt for units').grid(row = 36, column = 1)
        powerStepUnits = StringVar()
        self.powerStepUnitsEntry = Entry(self.master, textvariable = powerStepUnits).grid(row = 36, column = 2)
        self.powerStepButton = Button(self.master, text = 'Confirm power step', fg = 'blue', command = lambda: self.powerStep(powerStart, powerEnd, powerStep, powerStepUnits)).grid(row = 36, column = 3)

        
    def confirmPowerUnits(self, pu):
            powerUnits = pu.get()
            if(powerUnits != 'dbm' and powerUnits != 'watt'):
                    tkMessageBox.showinfo("Error", "Please make sure the units are either dbm or watt")
            elif(powerUnits == 'dbm'):
                    lm.write('sens1:pow:unit 0')
            elif(powerUnits == 'watt'):
                    lm.write('sens1:pow:unit 1')

    def getPowerLevel(self):
            pl1 = lm.query_ascii_values('fetch1:pow?')
            pl = pl1[0]
            plu = lm.query_ascii_values('sens1:pow:unit?')
            print(type(plu))
            print(plu)
            if(plu[0] == 0):
                    plUnits = 'dbm'
                    print plUnits
            elif(plu[0] == 1):
                    plUnits = 'watt'
                    print plUnits
            puLabel = Label(self.master, text = 'The power level is ' + str(pl) + ' ' + plUnits).grid(row = 12, column = 2)
    def confirmPowerSourceLevels(self, psl, psu):
            lm.write('OUTP!:pow:CONTR: on')
            powerLevel = psl.get()
            powerUnits = psu.get()

            if(powerUnits != 'dbm' and powerUnits != 'watt'):
                    tkMessageBox.showinfo("Error", "Please make sure the units are either dbm or watt")
            elif(powerUnits == 'dbm'):
                    lm.write('sour2:power:unit 0')
                    if(powerLevel < 6 or powerLevel > 14.77):
                            tkMessageBox.showinfo("error", 'The power level must be between 6 and 14.77 dbm')
                    else:
                            lm.write('sour2:pow ' + str(powerLevel))
            elif(powerUnits == 'watt'):
                    lm.write('sour2:power:unit 1')
                    if(powerLevel< .00398 or powerLevel > .03):
                            tkMessageBox.showinfo('Error', 'The power level must be between .00398 and .03 watts')
                    else:
                            lm.write('sour2:pow ' +str(powerLevel))
           
                
    def confirmWL(self, wavelength):
            wl = wavelength.get()
            if(wl < 1463 or wl> 1577):
                    tkMessageBox.showinfo("Error", 'Please make sure the wavelength is  between 1463 and 1577 nm')
            else:
                    lm.write('sour2:wav ' + str(wl) + 'NM')
                    

    def confirmSweep(self, wlStart, wlEnd, wlStep, wlTime):

            start = wlStart.get()
            initial = start
            end = wlEnd.get()
            step = wlStep.get()
            stepTime = wlTime.get()
            lm.write('source2:chan1:pow:state 1')
            wlList = []
            plList = []
            if(start < 1463 or start> 1577):
                    tkMessageBox.showinfo("Error", 'Please make sure the wavelength is  between 1463 and 1577 nm')

            if(end < 1463 or end> 1577):
                    tkMessageBox.showinfo("Error", 'Please make sure the wavelength is  between 1463 and 1577 nm')
                
            
            if(end > start):
                    diff = int((end-start) / step)
                            
                    while(end >= start):
                            lm.write('sour2:wav ' + str(start) + 'NM')
                            pl1 = lm.query_ascii_values('fetch1:pow?')
                            wlList.append(start)
                            start = start + step                    
                            plList.append(pl1[0])
                            sleep(stepTime)
                    plt.plot(wlList, plList)
                    print wlList
                    plt.xlabel('Nanometers')
                    plu = lm.query_ascii_values('sens1:pow:unit?')
                    if(plu[0] == 0):
                            plUnits = 'dbm'
                    elif(plu[0] == 1):
                            plUnits = 'watt'
                    plt.ylabel(str(plUnits))
                    with open('LM Wavelength Sweep.txt', 'w'):pass
                    lmFile = open('LM Wavelength Sweep.txt', 'a')
                    lmFile.write('Start sweep = ' + str(initial)+ '\n')
                    lmFile.write('End sweep = ' + str(end)+ '\n')
                    lmFile.write('Sweep step = '  + str(step)+ '\n')
                    lmFile.write('Power units = ' + plUnits+ '\n')
                    
                    for i in range(len(wlList)):
                            lmFile.write(str(wlList[i]) + ' ' + str(plList[i]) + '\n')
                    lmFile.close()
                    plt.show()
            if(start > end):
                    diff = int((start-end)/step)
                    while(start >= end):
                            print start
                            print end
                            lm.write('sour2:wav ' + str(start) + 'NM')
                            pl1 = lm.query_ascii_values('fetch1:pow?')
                            wlList.append(start)
                            start = start - step
                            plList.append(pl1[0])
                            sleep(stepTime)
                    
                    plt.plot(wlList, plList)
                    print wlList
                    plt.xlabel('Nanometers')
                    plu = lm.query_ascii_values('sens1:pow:unit?')
                    if(plu[0] == 0):
                            plUnits = 'dbm'
                    elif(plu[0] == 1):
                            plUnits = 'watt'
                    plt.ylabel(str(plUnits))
                    
                    with open('LM Wavelength Sweep.txt', 'w'):pass
                    lmFile = open('LM Wavelength Sweep.txt', 'a')
                    lmFile.write('Start sweep = ' + str(initial)+ '\n')
                    lmFile.write('End sweep = ' + str(end)+ '\n')
                    lmFile.write('Sweep step = '  + str(step)+ '\n')
                    lmFile.write('Power units = ' + plUnits+ '\n')
                    
                    for i in range(len(wlList)):
                            lmFile.write(str(wlList[i]) + ' ' + str(plList[i]) + '\n')
                    lmFile.close()
                    plt.show()
                

    def syncwl(self, syncWl):
            wl = syncWl.get()
            if(wl < 1463 or wl > 1577):
                    tkMessageBox.showinfo("Error", 'Please make sure the wavelength is  between 1463 and 1577 nm')
            else:
                    lm.write('sour2:wav ' + str(wl) + 'NM')
                    lm.write('sens1:pow:wav ' + str(wl) + 'nm')
                    
            
    def controlLaser(self, lOn):
            status= lOn.get()
            if(status != 'on' and status != 'off'):
                    tkMessageBox.showinfo('Error', 'The laser must either be off or on')
            elif(status == 'on'):
                    lm.write('source2:chan1:pow:state 1')
            elif(status == 'off'):
                    lm.write('source2:chan1:pow:state 0')

    def powerStep(self, powerStart, powerEnd, powerStep, powerStepUnits):
            units = powerStepUnits.get()
            step = powerStep.get()
            powerStepList = []
            powerMeasureList = []
            lm.write('source2:chan1:pow:state 1')
            if(units != 'watt' and units != 'dbm'):
                    tkMessageBox.showinfo("Error", 'Please make sure the units are watt or dbm')
            elif(units =='watt'):
                    lm.write('sens1:pow:unit 1')
                    lm.write('sour2:power:unit 1')
                    if(powerStart.get()< .00398 or powerStart.get() > .03):
                            tkMessageBox.showinfo('Error', 'The power must be between .00398 and .03 watts')
                    else:
                            
                            start = powerStart.get()
                            initial = start
                    if(powerEnd.get() < .00398 or powerEnd.get() > .03):
                            tkMessageBox.showinfo('Error', "The power must be between .00398 and .03 watts")
                    else:
                            end = powerEnd.get()
                            ending = end
            elif(units == 'dbm'):
                    lm.write('sens1:pow:unit 0')
                    lm.write('sour2:power:unit 0')                              
                    if(powerStart.get() < 6 or powerStart.get() > 14.77):
                            tkMessageBox.showinfo('Error', 'The power must be between 6 and 14.77 dbm')
                    else:
                            start =powerStart.get()
                            initial = start
                    
                    if(powerEnd.get() < 6 or powerEnd.get() > 14.77):
                            tkMessageBox.showinfo('Error', 'The power must be between 6 and 14.77 dbm')
                    else:
                           
                            end =powerEnd.get()
                            ending = end
            if(end > start):
                    while(end >= start):
                            lm.write('sour2:pow ' +str(start))
                            pMeasurement = lm.query_ascii_values('fetch1:pow?')
                            powerStepList.append(start)
                            powerMeasureList.append(pMeasurement[0])
                            start = start + step
                            sleep(1)
                    if(units == 'watt'):
                            lm.write('sour2:pow ' + str(end))
                            pMeasurement = lm.query_ascii_values('fetch1:pow?')
                            powerStepList.append(end)
                            powerMeasureList.append(pMeasurement[0])
                    plt.plot(powerStepList, powerMeasureList)
                    plt.xlabel('Output Power ' + str(units))
                    plt.ylabel('Measured Power ' + str(units))
                    with open('LM Power Sweep.txt', 'w'):pass
                    powerFile = open('LM Power Sweep.txt', 'a')
                    powerFile.write('Start sweep = ' + str(initial)+ '\n')
                    powerFile.write('End sweep = ' + str(ending)+ '\n')
                    powerFile.write('Sweep step = '  + str(step)+ '\n')
                    powerFile.write('Power units = ' + str(units) + '\n')
                    
                    for i in range(len(powerStepList)):
                            powerFile.write(str(powerStepList[i]) + ' ' + str(powerMeasureList[i]) + '\n')
                    powerFile.close()
                    plt.show()                


                    
            elif(start > end):
                    while(start >= end):
                            lm.write('sour2:pow ' + str(start))
                            pMeasurement = lm.query_ascii_values('fetch1:pow?')
                            powerStepList.append(start)
                            powerMeasureList.append(pMeasurement[0])
                            start = start - step
                            sleep(1)
                    plt.plot(powerStepList, powerMeasureList)
                    plt.xlabel('Output Power ' +str(units))
                    plt.ylabel('Measured Power ' + str(units))
                    with open('LM Power Sweep.txt', 'w'):pass
                    powerFile = open('LM Power Sweep.txt', 'a')
                    powerFile.write('Start sweep = ' + str(initial)+ '\n')
                    powerFile.write('End sweep = ' + str(ending)+ '\n')
                    powerFile.write('Sweep step = '  + str(step)+ '\n')
                    powerFile.write('Power units = ' + str(units) + '\n')
                    
                    for i in range(len(powerStepList)):
                            powerFile.write(str(powerStepList[i]) + ' ' + str(powerMeasureList[i]) + '\n')
                    powerFile.close()
                    plt.show() 
                    
                            
            

        
    def quitLM(self):
        lm.write('source2:chan1:pow:state 0')    
        self.master.destroy()

#class to control the gantry crane
class Gantry:
    current_position = [0.0, 0.0, 0.0]
    qLimit = [0.0, 0.0, 0.0]
    pause_queue = False
    
    def __init__(self,master):
        print("Init gantry on : " + str(eco1On))
        print("Init gantry on : " + str(polluxOn))        
        qLimit = eco1.query('-1 pos ').split()
        qLimit[0] = float(qLimit[0])
        qLimit[1] = float(qLimit[1])
        qLimit[2] = float(qLimit[2])
        #sets up the window, calibrate the xyz movement to start at (0,0,0)
        self.master = master
        self.master.geometry('1300x950+50+50')
        self.master.title('Gantry System')
        self.button1 = Button(self.master, text = "QUIT", fg = 'blue',command = self.quitGantry).grid(row=6,column=20)
        pollux.query('1 getpitch ')
        eco1.write("cal ")
        self.wait()

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

        #displays on screen the coordinates in (x,y,z) coordinates
        self.getCoordinate = Button(self.master, text = "Get coordinates of gantry system", fg = 'blue', command = lambda:self.getCoordinates()).grid(row=29, column = 5)

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

        self.pauseQueueButton = Button(self.master, text = "Begin Building Macro", fg = 'blue', command = lambda: self.pauseQueue()).grid(row=42, column=1)
        self.runQueueButton = Button(self.master, text = "Run Macro", fg = 'blue', command = lambda: self.startQueue()).grid(row=43, column = 1)

        fileName = StringVar()
        self.fileNameBox = Entry(self.master, textvariable = fileName).grid(row = 43, column = 4)
        self.saveMakroButton = Button(self.master, text = "Save Makro to file: ", fg = 'red', command = lambda: self.saveMakro(fileName)).grid(row=43, column=3)

        self.runFileButton = Button(self.master, text = "Run Makro from file", fg = 'red', command = lambda: self.runMakroFromFile()).grid(row=45, column=3)


        self.OPMRLabel = Label(self.master, text = 'Please specify the units for the optical power meter as dBm or mW: ').grid(row = 47, column = 1)
        opmrUnits = StringVar()
        self.OPMREntry = Entry(self.master, textvariable = opmrUnits).grid(row = 47, column = 2)
        self.turnOnOPMRButton = Button(self.master, text = 'Turn on 1830-R Optical Power Meter', fg = 'blue', command = lambda: self.turnOn1830R(opmrUnits)).grid(row = 47, column =3)
        self.turnOffOPMRButton = Button(self.master, text = 'Turn Off the 1830-R Optical Power Meter', fg = 'blue', command = lambda: self.turnOff1830R()).grid(row = 47, column = 4)
        self.clearPowerFile = Button(self.master, text = 'Clear Power File Measurements', fg = 'blue', command = lambda : self.clearFile()).grid(row = 47, column = 5)
        self.readingsHelpLabel = Button(self.master, text = 'Help', fg = 'blue', command = lambda : self.readingsHelp()).grid(row = 47, column = 6)

        self.getLargestPowerLevel = Button(self.master, text = 'Get power level and location', fg = 'blue', command = lambda: self.getLargestLevel()).grid(row = 49, column = 5)

        
        #runs the command queue periodically
        self.id = self.master.after(100, self.runEco1Queue)

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
            file = open('PowerMeasurement.txt', 'r')
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            for line in file:
                    words = line.split()                    
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

            ax.set_xlabel('X Label')
            ax.set_ylabel('Y Label')
            ax.set_zlabel('Z Label')

            plt.show()
            file.close()

    def readingsHelp(self):
            tkMessageBox.showinfo("Welcome to the help window", "When using the power readings, you must specify the units before clicking turn on device, the units can be mW or dBm \n \n After clicking turn on, anytime you move the gantry system, the power readings at that location will be written to a file on the desktop called PowerMeasurement.txt The units will displayed at the top. \n \n To clear the file, you can either type in a different unit into the turn on box or click the clear file button. \n \n Clicking the get power level button will go through the current power measurement file and pick out the highest power level, it will then display that level as well as the coordinates those values are at.")

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

    def runFunction(self, equation, increment, upperX, upperY, upperZ):
   
        eq = equation.get()
        upperX = upperX.get()
        if (upperX <= 0 or upperX > 103.48883):
            upperX = 103.48883
        upperY = upperY.get()
        if (upperY <= 0 or upperY > 28.42532):
            upperY = 28.42532
        upperZ = upperZ.get()
        if (upperZ <= 0 or upperZ > 103.42532):
            upperZ = 103.42532
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
            #eco1Queue.clear()
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
                        #try:
                        self.wait()
                        if(opmrOn == True):
                             self.takeMeasurement()
                        self.runEco1Item(item[0], item[1])
                        print(self.current_position)
                        
                        '''
                        except:
                            eco1Queue.appendleft(item)
                            tkMessageBox.showinfo('Error', 'Something went wrong, please restart the program and make sure all devices are connected properly. Any unexecuted commands will be saved in RECOVERY.txt.')
                            self.saveMakro('RECOVERY')
                            eco1On = polluxOn = False
                            eco1Queue.clear()
                            self.quitGantry()
                            app.finish()
                            return
                        '''
                    else:
                        try:
                            self.getCoordinates() #Once queue is done, refreshes the virtual position qLimit to the actual gantry position to ensure accuracy.
                        except:
                            tkMessageBox.showinfo('Error', 'Something went wrong, please restart the program and make sure all devices are connected properly. Any unexecuted commands will be saved in RECOVERY.txt.')
                            self.saveMakro('RECOVERY')
                            eco1On = polluxOn = False
                            eco1Queue.clear()
                            self.quitGantry()
                            app.finish()
                            return

                        self.qLimit[1] = float(self.current_position[1])
                        self.qLimit[2] = float(self.current_position[2])
                        self.qLimit[0] = float(self.current_position[0])

            self.id = self.master.after(10, self.runEco1Queue)

    def runEco1Item(self, string, command):
            print(string)
            if (command == 'w'):
                    eco1.write(string)
                    print 'wrote string command.'
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
                    
                    self.getCoordinates()
                    print new_position
                    print self.current_position
                    while (abs(new_position[0] - self.current_position[0]) > .1 or abs(new_position[1] - self.current_position[1]) > .1 or abs(new_position[2] - self.current_position[2]) > .1):
                        eco1.write('clear ')
                        eco1.write(string)
                        self.getCoordinates()
                        print 'got coordinates again: '
                        print self.current_position
   
            elif (command == 'r'):
                    eco1.read(string)
            elif (command == 'q'):
                    eco1.query(string)
            elif (command == 'measure'):
                    #get reading from sensor device
                    k = 9 # <-dummy code
            print 'about to clear, done running item'

            self.wait()
            eco1.write('clear ')

    #quits the gantry window, clears the stack of commands, and resets the device.
    def quitGantry(self):

        plt.close()
        eco1.write("clear ")
        eco1.write("reset ")
        eco1.close()
        pollux.close()
    
        print("wow, it closed!")

        print("quit gantry eco : " + str(eco1On))
        print("quit gantry pollux : " + str(polluxOn))    
        self.master.destroy()

def main():
    root=Tk()
    global app
    app = gpibMain(root)
    root.mainloop()

if __name__ == '__main__':
    main()
