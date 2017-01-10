import visa
from time import sleep
from time import time
from math import*
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

lwmOn = False
rm = visa.ResourceManager()
resources = rm.list_resources()
try:
    lwm = rm.open_resource("TCPIP0::10.4.27.204::inst0::INSTR")
    lwmOn = True
except:
    lwmOn = False
inp = '*IDN?'
typ = 'q'
lwm.timeout = None
while(inp != ''):
    if (typ == 'q'):
        print lwm.query(inp)
    elif (typ == 'w'):
        print lwm.write(inp)
    elif (typ == 'r'):
        print lwm.read()
    last = inp
    inp = raw_input('command: ').strip()
    typ = raw_input('type (q/w/r): ').strip()
    if inp == '_':
        inp = last
    #print lwm.write("OUTP1:POW:UN DBM")
    #print lwm.query("fetc1:pow?").strip()

def laserOnOff(lOn):
    status = lOn[0]
    if(status != '1' and status != '0'):
        print "Error: the laser must either be off(0) or on(1)"
    elif(status == '1'):
        lwm.write('sour2:chan1:pow:state 1')
    elif(status == '0'):
        lwm.write('sour2:chan1:pow:state 0')

#validate functions make sure that the input from the user is in the correct bounds for the device, else it will show an error message giving the correct bounds.
def validateWV(): 
    wl = float(raw_input('Set fixed wavelength: '))
    if(wl < 1463 or wl > 1577):
        print 'Please make sure the wavelength is between 1463 and 1577 nm'
        validateWV()
    else:
        lwm.write('sour2:wav ' + str(wl) + 'NM')
#####################################################################################

def showHelp():
    print "Helpful Information: \
          \n The wavelength must be between 1463 and 1577 nm \n \
          \n When using the power level, you must specift the units as either dBm(d) or Watt(w) \n \
          \n If using dBm, you must be between -20 and 8 dBm, while for mW you have to be between .01 and 6.31 mW \n \
          \n The starting and ending bounds for the sweep are both in nanometers and must fall between 1480 and 1580 nm \n \
          \n  When using the step mode, please specify a step amount in nm between .001 and 100 as well as a time between each step in seconds from .01 to 999 seconds \n \
          \n When using continuous time, leave the sweep step and sweep step time as 0, the continuous time is how long it takes to step through the range and must be between 1 and 99999 seconds\n \
          \n You can also do a stepping sweep with power, you must specify the power as either mW or dBm, all the other parameters are the same."

def validatePW(): # Ask user for new power level. ###################################
    powerUnits = raw_input('Set units (Watt/dBm): ').strip().lower()
    
    if(powerUnits == '' or (powerUnits[0] != 'd' and powerUnits[0] != 'w')):
        print "Please make sure the units are either dbm(d) or watt(w)."
        validatePW()
        return
    
    powerLevel = float(raw_input('Set power level: '))
    if(powerUnits[0] == 'd'):
        lwm.write('sour2:pow:unit 0')
        if(powerLevel < 5.999 or powerLevel > 14.771):
            print 'The power level must be between 5.999 and 14.771 dbm, inclusive.'
        else:
            lwm.write('sour2:pow ' + str(powerLevel))
    elif(powerUnits[0] == 'w'):
        lwm.write('sour2:pow:unit 1')
        if (powerLevel < .00398 or powerLevel > .03):
            print 'The power level must be between .00398 and .03 watts'
        else:
            lwm.write('sour2:pow ' + str(powerLevel))

        
#####################################################################################

def validateFreq():
    fIn = float(raw_input("Set frequency (THz): "))
    #aq.write('TSTEPU1')
    if fIn < 189.7421 or fIn > 202.5625:
        print "Error: the frequency must be between 189.7421 THz and 202.5625 THz."
    else:
        #aq.write("TFR " + '%.4f' % fIn)
        print ""

def setStepSize():
    stepSize = raw_input("Step size (nm): ").strip()
    if stepSize == "" or float(stepSize) == 0.0:
        stepSize = 1
    else:
        stepSize = float(stepSize)
    if (stepSize >= .001 and stepSize <= 114):
        lwm.query("sour2:wav:swe:step " + "%.3f" % stepSize + "nm")
        print ""
    else:
        print "Error: discrete step time must be between 0.1 and 999.0 seconds."

def setStepTime():
    stepTime = raw_input("Step time (blank for continuous): ").strip()
    if stepTime == "" or float(stepTime) == 0.0:
        contTime = float(raw_input("Total length (continuous sweep): "))
        stepTime = 0.0
    else:
        stepTime = float(stepTime)
    stepFlag = False
    if (stepTime == 0):
        #aq.write('TSWET ' + '%.2f' % contTime)
        print "Continuous sweep not yet supported."
    elif (stepTime > .01 and stepTime < 999):
        #aq.write('TSTET ' + '%.2f' % stepTime)
        return stepTime
    else:
        print "Error: discrete step time must be between 0.1 and 999.0 seconds."

def setStartWV():
    start = float(raw_input("Start wavelength: "))
    if(start < 1463.000 or start > 1577.000):
        print "Error: value must be between 1463.000 and 1577.000 nm."
    else:
        lwm.write("sour2:wav:swe:star " + '%.3f' % start + 'NM')


def setEndWV():
    end = float(raw_input("End wavelength: "))
    if(end < 1480.000 or end > 1580.000):
        print "Error: value must be between 1480.000 and 1580.000 nm."
    else:
        lwm.write("sour2:wav:swe:stop " + '%.3f' % end + 'NM')

###### Takes out scientific notation ######
def filterEE(measurement):
    if 'E' in measurement:
        m_list = measurement.split("E")
        return float(m_list[0]) * (10 ** float(m_list[1]))
    else:
        return float(measurement)

def setSample():
    title = raw_input('Please enter the sample used : ').strip()
    plt.title('' + str(title))
    return title
    

def main():
    if not lwmOn:
        print "Please connect Lightwave Multimeter to the LAN network and try again."
        return
    #Show current laser parameters
    step_time = start_wv = end_wv = freq = dbm = mw = wl = wv_step = 0
    title = 'Unknown' 

    while(True):
        lwm.write('sour2:pow:unit 0')
        dbm = lwm.query('sour2:pow?').strip()
        sleep(.1)
        lwm.write('sour2:pow:unit 1')
        mw = lwm.query("sour2:pow?").strip()
        sleep(.1)
        wl = str(filterEE(lwm.query('sour2:wav?').strip())*1000000000)
        sleep(.1)
        #freq = aq.query("TFR?").strip()
        #sleep(.1)
        start_wv = str(filterEE(lwm.query("sour2:wav:swe:star?").strip())*1000000000)
        sleep(.1)
        end_wv = str(filterEE(lwm.query("sour2:wav:swe:stop?").strip())*1000000000)
        sleep(.1)
        step_time = 1 #default step time
        sleep(.1)
        wv_step = str(filterEE(lwm.query("sour2:wav:swe:step?").strip())*1000000000)

        print "\nCURRENT LIGHTWAVE MULTIMETER PARAMETERS: "
        print "Power: " + dbm + "dBm / " + mw + " mW"
        print "Wavelength: " + wl + " nm"
        #print "Frequency: " + freq + " THz \n"

        print "SWEEP SETTINGS:"
        print "Start wavelength: " + start_wv + " nm"
        print "End wavelength: " + end_wv + " nm"
        print "Step time: " + str(step_time) + " s"
        print "Step size: " + wv_step + " nm \n"
        print "Sample : " + title
        

        response = raw_input("Do you want to change any parameters? Press Enter to skip. (Power [p], Wavelength [w], Step Time [st], Step Size [ss], Start Wavelength [sw], End Wavelength [ew], Sample [s])").strip().lower()
        if (response == ''):
            break
        elif (response[0] == 'p'):
            validatePW()
        elif (response[0] == 'w'):
            validateWV()
        #elif (response[0] == 'f'):
        #    validateFreq()
        elif (response == 'st'):
            step_time = setStepTime()
        elif (response == 'ss'):
            setStepSize()
        elif (response == 'sw'):
            setStartWV()
        elif (response == 'ew'):
            setEndWV()
        elif ( response == 's'):
            title = setSample()

    duration = (float(end_wv) - float(start_wv) + float(wv_step)) * float(step_time) / float(wv_step)
    print "This will scan for: " + str(duration) + " seconds."

    ########## Asks about saving to text file. ########################################
    file_save = raw_input("Do you want to save this data to a text file? (y/n) ").strip()
    if file_save == "":
        file_save = "n"
    if file_save[0].lower() == "y":
        name = raw_input("Name of new data file (leaving blank appends to 'PowerMeasurement.txt'): ").strip()
        if name == "":
            powerFile = open('C:\\Users\\User\\Desktop\\Power Measurement Files\\PowerMeasurement.txt', "a")
        else:
            powerFile = open('C:\\Users\\User\\Desktop\\Power Measurement Files\\' + name + '.txt', "w")
    ###################################################################################

    #Running discrete sweep
    step_time = float(step_time)
    wavelength = start_wv = float(start_wv)
    wv_step = float(wv_step)
    end_wv = float(end_wv)
    wlList = []
    #total = start_time = end_time = 0
    #wl_change = hit = False
    interval_timer = average = total_valid = count_valid = 0

    #lwm.write('sour2:wav:swe:mode MAN')
    
    check_params = lwm.query('sour2:wav:swe:chec?')
    print check_params
    if (check_params.strip() != '0,OK'):
        trash = raw_input("Params are unacceptable, program will restart now. Press Enter.")
        print '\n\n\n'
        main()
        return
    
        
    print "\nRunning sweep."
    lwm.write('source2:chan1:pow:state 1')
    lwm.write('source2:pow:state 1')
    lwm.write('sour2:wav ' + str(wavelength) + 'NM')
    lwm.write('sens1:pow:wav ' + str(wavelength) + 'NM')
    sleep(5)
    #lwm.write('sour2:pow 230 uW')
    #lwm.write('sour2:wav:swe STAR')
    sleep(.3)
    # Increments each wavelength step. ###################
    for i in range(int((end_wv - start_wv)/wv_step)+1):
        print i
        #print 'made it to the top'
        lwm.write('sour2:wav ' + str(wavelength) + 'NM')
        lwm.write('sens1:pow:wav ' + str(wavelength) + 'NM')
        sleep(step_time)
        num = lwm.query_ascii_values('fetch1:pow?')
        wavelength += wv_step     
    
        measurement = str(num[0])


        measurement = filterEE(measurement)
        plt.scatter(start_wv + wv_step * i, measurement, c='blue', alpha='.5')
        if file_save == "y":
            powerFile.write(str(start_wv + wv_step * i) + ' nm, ' + str(measurement) + '\n')
        
    ######################################################

    if file_save == "y":
        powerFile.close()

    plt.xlabel('wavelength (nm)')
    plt.ylabel('amplitude (units on power meter)')
    
    plt.grid(True)
    if lwmOn: lwm.close()
    print "Finished!"
    plt.show()
    plt.close()
    #lwm.write('sour2:wav:swe STOP')

main()
if lwmOn: lwm.close()
