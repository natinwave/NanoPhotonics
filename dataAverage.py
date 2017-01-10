from tkFileDialog import askopenfilename
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter




#fileLoad = int(raw_input("Enter 0 if you want to add another file"))
#print fileLoad
fileLoad = 0
fileCounter = 0
powerArray =  115 * [0]
wvArray = 115 * [0]
k = 0

wvStart = 1467

for i in range(115):
    wvArray[i] = wvStart
    wvStart += 1

while(fileLoad == 0):
    
    fileName = askopenfilename()
    file = open(fileName, 'r')
   
            
    for line in file:        
        line = line.split(', ')
        powerArray[k] += float(line[1])
        k+=1
    print powerArray    
    fileCounter += 1    
    file.close()
    k=0
           
    
    fileLoad = int(raw_input("Enter 0 if you want to add another file, or 1 to average the data "))
    

j = 0





for j in range(len(powerArray)):
    
    powerArray[j] = powerArray[j] / fileCounter


    
print powerArray

plt.plot(wvArray, powerArray)
plt.show()
