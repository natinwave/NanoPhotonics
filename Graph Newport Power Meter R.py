import visa
from time import sleep
from time import time
from math import*
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

rm = visa.ResourceManager()
resources = rm.list_resources()
opmOn = True
if 'GPIB0::4::INSTR' in resources:
    opmr = rm.open_resource('GPIB0::4::INSTR')
elif 'GPIB::4::INSTR' in resources:
    opmr = rm.open_resource('GPIB::4::INSTR')
else:
    print "Please make sure the newport power meter is plugged in via GPIB and its address is set to '4.'"
    sleep(4)
    opmOn = False

aqOn = True
if 'GPIB0::20::INSTR' in resources:
    aq = rm.open_resource('GPIB0::20::INSTR')
elif 'GPIB::20::INSTR' in resources:
    aq = rm.open_resource('GPIB::20::INSTR')
elif 'ASRL1::INSTR' in resources:
    aq = rm.open_resource('ASRL1::INSTR')
else:
    print "To get data that relates amplitude to frequency, please make sure the AQ4321A is plugged in via GPIB and its address is set to '20.'"
    aqOn = False


#validate functions make sure that the input from the user is in the correct bounds for the device, else it will show an error message giving the correct bounds.
def validateWV(self, wavelength_in):
    aq.write('TSTEPU0')    
    s = float(raw_input('Set fixed wavelength: '))
    if(s < 1480 or s > 1580):
        print "Error: please keep the wavelength between 1480.000 and 1580.000 nm."

    else:
        aq.write("TWL " + '%.3f' % s)


def showHelp():
    print "Helpful Information: \
          \n The wavelength must be between 1480 and 1580 nm \n \
          \n When using the power level, you must specift the units as either dBm or mW \n \
          \n If using dBm, you must be between -20 and 8 dBm, while for mW you have to be between .01 and 6.31 mW \n \
          \n The starting and ending bounds for the sweep are both in nanometers and must fall between 1480 and 1580 nm \n \
          \n  When using the step mode, please specify a step amount in nm between .001 and 100 as well as a time between each step in seconds from .01 to 999 seconds \n \
          \n When using continuous time, leave the sweep step and sweep step time as 0, the continuous time is how long it takes to step through the range and must be between 1 and 99999 seconds\n \
          \n You can also do a stepping sweep with power, you must specify the power as either mW or dBm, all the other parameters are the same."

def validatePW():
    uIn = raw_input('Set units (mW/dBm): ').strip()
    pIn = float(raw_input('Set power level: '))

    if(uIn[0].lower() == "d"):
        if(pIn < -20 or pIn > 8):
            print "Error: the power level must be between -20 dBm and 10 dBM."
        else:
            aq.write("TPDB " + '%.1f' % pIn)
    if(uIn[0].lower() == "m"):
        if(pIn < .010 or pIn > 7.943):
            print "Error: the power level must be between .010 mW and 7.943 mW."
        else:
            aq.write("TPMW " + '%.3f' % pIn)
    else:
        print "Error: the units must be in dBm or mW. Can be entered as 'd' or 'm.'"

def validateFreq():
    fIn = float(raw_input("Set frequency (THz): "))
    aq.write('TSTEPU1')
    if fIn < 189.7421 or fIn > 202.5625:
        print "Error: the frequency must be between 189.7421 THz and 202.5625 THz."
    else:
        aq.write("TFR " + '%.4f' % fIn)

def setStepSize():
    stepSize = raw_input("Step size (nm): ").strip()
    if stepSize == "" or float(stepSize) == 0.0:
        stepSize = 1
    else:
        stepSize = float(stepSize)
    if (stepSize >= .001 and stepSize <= 100):
        aq.write('TSTEWL' + '%.3f' % stepSize)
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
        aq.write('TSWET ' + '%.2f' % contTime)
    elif (stepTime > .01 and stepTime < 999):
        aq.write('TSTET ' + '%.2f' % stepTime)
    else:
        print "Error: discrete step time must be between 0.1 and 999.0 seconds."

def setStartWV():
    start = float(raw_input("Start wavelength: "))
    if(start < 1480.000 or start > 1580.000):
        print "Error: value must be between 1480.000 and 1580.000 nm."
    else:
        aq.write('TSTAWL ' + '%.3f' % start)
        aq.write('WAIT0.1')

def setEndWV():
    end = float(raw_input("End wavelength: "))
    if(end < 1480.000 or end > 1580.000):
        print "Error: value must be between 1480.000 and 1580.000 nm."
    else:
        aq.write('TSTPWL ' + '%.3f' % end)
        aq.write('WAIT0.1')

def main():
    if not opmOn:
        return
    #Show current laser parameters
    step_time = start_wv = end_wv = freq = dbm = mw = wl = wv_step = 0

    while(True):
        if aqOn:
            dbm = aq.query("TPDB?").strip()
            sleep(.1)
            mw = aq.query("TPMW?").strip()
            sleep(.1)
            wl = aq.query("TWL?").strip()
            sleep(.1)
            freq = aq.query("TFR?").strip()
            sleep(.1)
            start_wv = aq.query("TSTAWL?").strip()
            sleep(.1)
            end_wv = aq.query("TSTPWL?").strip()
            sleep(.1)
            step_time = aq.query("TSTET?").strip()
            sleep(.1)
            wv_step = aq.query("TSTEWL?").strip()

            print "\nCURRENT AQ4321 PARAMETERS: "
            print "Power: " + dbm + "dBm / " + mw + " mW"
            print "Wavelength: " + wl + " nm"
            print "Frequency: " + freq + " THz \n"

            print "SWEEP SETTINGS:"
            print "Start wavelength: " + start_wv + " nm"
            print "End wavelength: " + end_wv + " nm"
            print "Step time: " + step_time + " s"
            print "Step size: " + wv_step + " nm \n"

            response = raw_input("Do you want to change any parameters? Press Enter to skip. (Power [p], Wavelength [w], Step Time [st], Step Size [ss], Start Wavelength [sw], End Wavelength [ew])").strip().lower()
            if (response == ''):
                break
            elif (response[0] == 'p'):
                validatePW()
            elif (response[0] == 'w'):
                validateWV()
            elif (response[0] == 'f'):
                validateFreq()
            elif (response == 'st'):
                setStepTime()
            elif (response == 'ss'):
                setStepSize()
            elif (response == 'sw'):
                setStartWV()
            elif (response == 'ew'):
                setEndWV()
        else:
            print "AQ laser source is not connected."
            break

    duration = raw_input("How many seconds should this scan for? (Press Enter to calculate automatically)")
    if duration == "":
        sleep(.5)
        duration = (float(end_wv) - float(start_wv) + float(wv_step)) * float(step_time) / float(wv_step)
        print duration
    else:
        duration = float(duration)

    #samples per second for graph
    samples = 1.0
    file_save = raw_input("Do you want to save this data to a text file? (y/n) ").strip()
    if file_save == "":
        file_save = "n"
    if file_save[0].lower() == "y":
        name = raw_input("Name of new data file (leaving blank appends to 'PowerMeasurement.txt'): ").strip()
        if name == "":
            powerFile = open('C:\\Users\\User\\Desktop\\Power Measurement Files\\PowerMeasurement.txt', "a")
        else:
            powerFile = open('C:\\Users\\User\\Desktop\\Power Measurement Files\\' + name + '.txt', "w")

    #Running discrete sweep
    step_time = float(step_time)
    start_wv = float(start_wv)
    total = start_time = end_time = 0
    wl_change = hit = False
    interval_timer = average = total_valid = count_valid = 0
    if aqOn:
        print "\nRunning sweep."
        begin = time()
        #aq.write('TSGL')
        # For the length of the sweep times the number of samples. i occurs "samples" times per second
        for i in range(int(duration * samples)):
            start_time = time()
            measurement = opmr.query('D?')
            
            if (i / samples) % step_time == 0:
                wavelength += float(wv_step)
                aq.write("TFR " + '%.4f' % wavelength)
                wl = str(wavelength)
                wl_change = True
                interval_timer = 0
                opmr.write('W' + wl)
            else:
                wl_change = False
                interval_timer += 1
                
            ###### Takes out scientific notation ######
            if 'E' in measurement:
                m_list = measurement.split("E")
                measurement = float(m_list[0]) * (10 ** float(m_list[1]))
            else:
                measurement = float(measurement)
            ###########################################

            #####
            if (interval_timer / samples > .3 and interval_timer / samples < .9 and not wl_change):
                hit = True
                total_valid += measurement
                count_valid += 1
                plt.scatter(wl, measurement, c='blue', alpha='.1')
            else:
                #plt.scatter(wl, measurement, c='red', alpha='.05')
                #calculates the average after each group of valid points have been measured.
                if (hit):
                    average = total_valid / count_valid
                    if file_save == "y":
                        #powerFile.write(str(start_wv + (int((i - 1) / samples) / int(step_time)) * float(wv_step)) + ' nm, ' + str(average))
                        powerFile.write(wl + ' nm, ' + str(average))
                        plt.scatter(wl, average, c='green')
                    total_valid = count_valid = 0
                    #opmr.write('W' + str(start_wv + int((int((i - 1) / samples) / int(step_time)) * float(wv_step))))
                    hit = False
                    
            end_time = time()
            if (1/samples - end_time + start_time > 0):
                sleep((1 / samples) - end_time + start_time)
                total += ((1 / samples) - end_time + start_time)
        end = time()
        print "total time: " + str(end - begin)
        print "total slept: " + str(total)
    else:
        for i in range(int(duration * samples)):
            sleep(1 / samples - end_time + start_time)
            start_time = time()
            measurement = opmr.query('D?')
            if file_save == "y":
                powerFile.write(str(i / samples) + ' nm, ' + str(measurement))
            if 'E' in measurement:
                m_list = measurement.split("E")
                measurement = float(m_list[0]) * (10 ** float(m_list[1]))
            else:
                measurement = float(measurement)
            plt.scatter((i / samples), measurement, c='blue')
            end_time = time()

    if file_save == "y":
        powerFile.close()

    plt.xlabel('wavelength (nm)')
    plt.ylabel('amplitude (units on power meter)')
    plt.grid(True)
    opmr.close()
    if aqOn: aq.close()
    print "Finished!"
    plt.show()
    plt.close()
    

main()
