from intensity_ratio_func import *
import os


outputfile = open('./time/intensity_time.txt','w')
outputfile.write('File\tAvgI(divide)\tSTD(divide)\tAvgI(subtract)\tSTD(subtract)\n')
for filename in os.listdir('./time'):
    if filename.endswith('.bmp'):
        intensity_divide,stddev_divide,intensity_subtract,stddev_subtract = IntensityRatio('./time/' + filename)
        outputfile.write(filename + '\t%.2f\t%.2f\t%.2f\t%.2f\n' % (intensity_divide,stddev_divide,intensity_subtract,stddev_subtract))
outputfile.close()
