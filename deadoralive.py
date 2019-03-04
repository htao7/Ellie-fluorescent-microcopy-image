from intensity_ratio_func import *
import os
import re


outputfile = open('./viability/viability.txt','w')
outputfile.write('Exp\tViability(divide)\tViability(subtract)\n')
for filename in os.listdir('./viability'):
    if filename.endswith('dapi.bmp'):
        num = re.findall(r'\d+', filename)[0]
        i_alive_divide,_,i_alive_subtract,_ = IntensityRatio('./viability/' + num + 'dapi.bmp')
        i_dead_divide,_,i_dead_subtract,_ = IntensityRatio('./viability/' + num + 'fitc.bmp')
        outputfile.write(num + '\t%.2f\t%.2f\n' % ((i_alive_divide / (i_alive_divide + i_dead_divide)), (i_alive_subtract / (i_alive_subtract + i_dead_subtract))))
outputfile.close()
