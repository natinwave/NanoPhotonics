from tkFileDialog import askopenfilename
import math
from matplotlib.ticker import LinearLocator, FormatStrFormatter


def main():
    filename = askopenfilename()
    file = open(filename, 'r')

    # converts dBm to mW
    input_power = .01 * math.pow(10, .1 * float(filename.split('@')[1].split('dBm.txt')[0]))

    output = open(filename.split('/')[-1].split('.txt')[0] + '[Transmission_Ratio].txt', 'w')

    for line in file:
        line = line.split(', ')
        print line
        print input_power
        output.write(line[0] + ', ' + str(float(line[1]) / input_power) + '\n')
        
    file.close()
    output.close()

    return

main()
