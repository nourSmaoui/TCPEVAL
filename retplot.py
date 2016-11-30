import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from xml.dom import minidom
direct = "../TCPEVAL/bbr10h/"
doc = minidom.parse(direct+"bbr-10h-10MB-40ms.xml")
name = doc.getElementsByTagName("topology")[0].getAttribute("name")

with open(direct+name+"reth3", "r") as ins:
    array1 = []
    for line in ins:
		print line.split(' ')
		try:
			array1.append(int(line.split(' ')[4]))
		except:
			print "error", line.split(' ')
        
with open(direct+name+"reth4", "r") as ins:
    array2 = []
    for line in ins:
		try:
			array2.append(int(line.split(' ')[4]))
		except:
			print "error", line.split(' ')
#~ with open("/home/bbr/cwnd3", "r") as ins:
    #~ array3 = []
    #~ for line in ins:
        #~ array3.append(int(line.split(':')[1]))
#        array.append()

N1 = len(array1)
ind1 = np.arange(N1)
N2 = len(array2)
ind2 = np.arange(N2)
#~ N3 = len(array3)
#~ ind3 = np.arange(N3)
#~ with open("/home/nour/Downloads/normal_indoor_change.txt", "r") as ins:
    #~ array2 = []
    #~ for line in ins:
        #~ array2.append(float(line.split(',')[2]))
#~ #        array.append()
#~ 
#~ N2 = len(array2)
#~ ind2 = np.arange(N2)
#~ 
#~ with open("/home/nour/Downloads/saturated.txt", "r") as ins:
    #~ array3 = []
    #~ for line in ins:
        #~ array3.append(float(line.split(',')[2]))
#~ #        array.append()
#~ 
#~ N3 = len(array3)
#~ ind3 = np.arange(N3)
#~ 
#~ with open("/home/nour/Downloads/dark.txt", "r") as ins:
    #~ array4 = []
    #~ for line in ins:
        #~ array4.append(float(line.split(',')[2]))
#~ #        array.append()
#~ 
#~ N4 = len(array4)
#~ ind4 = np.arange(N4)

fig = plt.figure()
axes = plt.gca()
#~ axes.set_xlim([xmin,xmax])
#~ axes.set_ylim([-64,64])
#~ axes.set_xlim([0,N1])
ax = fig.add_subplot(111)
#~ f2 = interp1d(ind1, array1, kind='cubic')
ax.plot(ind1/2, array1)
#ax.plot(inds1, ssthresh1)
ax.plot(ind2/2, array2)
plt1,=ax.plot(ind1/2,array1,label='flow 1')
plt2,=ax.plot(ind2/2,array2,label='flow 2')
#ax.plot(ind3, array3)
#~ ax.plot(ind2, array2)
#~ ax.plot(ind3, array3)
#~ ax.plot(ind4, array4)
#~ ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
#~ fig.autofmt_xdate()


plt.ylabel('retransmissions')
plt.xlabel('time(s)')
plt.legend(handles=[plt1,plt2])
fig.savefig(name+"-ret.pdf")

#~ x = np.linspace(0, 30)
#~ line, = plt.plot(x, array, '--', linewidth=2)
#~ 
#~ #dashes = [10, 5, 100, 5]  # 10 points on, 5 off, 100 on, 5 off
#~ #line.set_dashes(dashes)
#~ 
#~ plt.show()
