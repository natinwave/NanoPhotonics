from tkFileDialog import askopenfilename
import tkMessageBox
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

def main():
    colors = ['Blue', 'Green', 'Red', 'Magenta', 'Orange', 'Black', 'DarkCyan', 'Brown', 'Yellow', 'MediumSlateBlue']
    input = 'y'
    i = 0
    graphFile(colors[i])
    while (tkMessageBox.askyesno("Continue?", "Would you like to add another file to this graph?") and i < 10):
        i += 1
        graphFile(colors[i])
    
    plt.xlabel('wavelength (nm)')
    plt.ylabel('amplitude (units on power meter)')

    plt.grid(True)
    plt.show()
    plt.close()

def graphFile(color):

    filename = askopenfilename()
    file = open(filename, 'r')
    print filename
    wvArray = []
    powerArray = []
    for line in file:
        line = line.split(' nm, ')
        wvArray.append(float(line[0]))
        powerArray.append(float(line[1]))

    file.close()

    plt.plot(wvArray, powerArray, color)

main()

    
