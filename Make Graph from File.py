from tkFileDialog import askopenfilename
import tkMessageBox
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

patches = []

def main():
    
    colors = ['Blue', 'Green', 'Red', 'Magenta', 'Orange', 'Black', 'DarkCyan', 'Brown', 'Yellow', 'MediumSlateBlue']
    input = 'y'
    i = 0
    graphFile(colors[i])
    while (tkMessageBox.askyesno("Continue?", "Would you like to add another file to this graph?") and i < 10):
        i += 1
        graphFile(colors[i])
    
    plt.xlabel('wavelength (nm)')
    plt.ylabel('transmission ratio')

    plt.grid(True)
    plt.show()
    plt.close()

def graphFile(color):
    filename = askopenfilename(initialdir="C:\Users\User\Desktop\PowerMeasurementFiles")
    if filename == '':
        return
    file = open(filename, 'r')
    print filename
    wvArray = []
    powerArray = []
    for line in file:
        line = line.split(', ')
        wvArray.append(float(line[0]))
        powerArray.append(float(line[1]))

    file.close()
    patches.append(mpatches.Patch(color=color, label=filename.split("/")[-1].replace('.txt', '')))
    plt.legend(handles=patches)
    plt.plot(wvArray, powerArray, color) 

main()

    
