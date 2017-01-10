from tkFileDialog import askopenfilename
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

filename = askopenfilename()
file = open(filename, 'r')

filename2 = askopenfilename()
if filename2.strip() == "":
    filename2 = "C:\Users\User\Desktop\Power Measurement Files\10dBm Direct Full Spectrum"
    input_power = .01
else:
    input_power = float(raw_input("What was the input power of the calibration?"))

file2 = open(filename2, 'r')

output = open(filename.split('/')[-1].split('.txt')[0] + '_Calibrated.txt', 'w')

for line in file:
    line = line.split(', ')
    line2 = file2.readline().split(', ')
    if (line[0] != line2[0]):
        print 'Both sweeps must have the same range and step width.'
        break
    output.write(line[0] + ', ' + str(float(line[1]) * float(line2[1]) / input_power) + '\n')
    
file.close()
file2.close()
output.close()
