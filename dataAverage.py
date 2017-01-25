from tkFileDialog import askopenfilename
import matplotlib.pyplot as plt
from time import sleep
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

def loop(fileName, powerArray, wvArray):
    file = open(fileName, 'r')
    k = 0
    for line in file:        
        line = line.split(' nm , ')
        powerArray[k] += float(line[1])
        if wvArray[k] != '' and wvArray[k] != line[0]:
            print 'All files must have the same wavelength bounds.'
            sleep(3)
            return
        wvArray[k] = float(line[0])
        k+=1
 
    file.close()
    
    return [powerArray, wvArray]

def main(fileNameList):
    fileLoad = 0
    fileCounter = 0
    powerArray =  115 * [0]
    wvArray = 115 * [0]
    fileNames = []
    
    if len(fileNameList) != 0:
        for fileName in fileNameList:
            fileCounter += 1
            file = open(fileName, 'r')
            k = 0
            for line in file:        
                line = line.split(' nm , ')
                powerArray[k] += float(line[1])
                if wvArray[k] != '' and wvArray[k] != line[0]:
                    print 'All files must have the same wavelength bounds.'
                    sleep(3)
                    return
                wvArray[k] = float(line[0])
                k+=1
         
            file.close()
    else:
        while(fileLoad == 0):
            fileName = askopenfilename()
            fileNames.append(fileName)
            fileCounter += 1
            file = open(fileName, 'r')
            k = 0
            for line in file:        
                line = line.split(' nm , ')
                powerArray[k] += float(line[1])
                if wvArray[k] != '' and wvArray[k] != line[0]:
                    print 'All files must have the same wavelength bounds.'
                    sleep(3)
                    return
                wvArray[k] = float(line[0])
                k+=1
         
            file.close()
            fileLoad = int(raw_input("Enter 0 if you want to add another file, or 1 to average the data "))

    j = 0
    outputFile = fileName.split('@')[0]
    for name in fileNames:
        outputFile += name.split('@')[1].split('dBm.txt')[0] + ','
    output = open(outputFile + 'dBm[Averaged].txt', 'w')

    for j in range(len(powerArray)):
        
        powerArray[j] = powerArray[j] / fileCounter
        output.append(str(wvArray[j]) + ' nm, ' + str(powerArray[j]) + '\n')


    #print powerArray

    plt.plot(wvArray, powerArray)
    output.close()
    plt.show()
    return

main([])
