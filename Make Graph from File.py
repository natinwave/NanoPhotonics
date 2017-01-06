from tkFileDialog import askopenfilename
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

filename = askopenfilename()
file = open(filename, 'r')

for line in file:
    line = line.split(' nm, ')
    plt.scatter(float(line[0]), float(line[1]), c='blue', alpha='.5')

file.close()

plt.xlabel('wavelength (nm)')
plt.ylabel('amplitude (units on power meter)')

plt.grid(True)
print "Finished!"
plt.show()
plt.close()
