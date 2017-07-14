from tkFileDialog import askopenfilename
import math
from matplotlib.ticker import LinearLocator, FormatStrFormatter


def main():
    filename = askopenfilename()
    file = open(filename, 'r')

    # converts dBm to mW
    input_power = float(filename.split('@')[1].split('dBm.txt')[0])

    output = open('C:\\Users\\User\\Desktop\\Power Measurement Files\\' + filename.split('/')[-1].split('.txt')[0] + '[Transmission_Ratio].txt', 'w')

    for line in file:
        line = line.split(', ')
        print line
        print input_power
        output.write(line[0] + ', ' + str(float(line[1]) / input_power) + '\n')
        
    file.close()
    output.close()

    return

main()
