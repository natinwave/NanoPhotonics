from tkFileDialog import askopenfilename
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

filename = askopenfilename()
file = open(filename, 'r')

filename2 = askopenfilename()
file2 = open(filename2, 'r')

output = open('Difference_' + filename.split('/')[-1] + '__' + filename2.split('/')[-1] + '.txt', 'w')

for line in file:
    line = line.split(', ')
    line2 = file2.readline().split(', ')
    if (line[0] != line2[0]):
        print 'Both sweeps must have the same range and step width.'
        break
    output.write(line[0] + ', ' + str(float(line[1]) - float(line2[1]) * 0.0002252508044671588112814688623888) + '\n')
    

file.close()
file2.close()
output.close()
