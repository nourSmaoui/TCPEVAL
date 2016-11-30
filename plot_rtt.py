import matplotlib.pyplot as plt
import numpy as np
from xml.dom import minidom
direct = "../TCPEVAL/bbr10h/"
doc = minidom.parse(direct+"bbr-10h-10MB-40ms.xml")
name = doc.getElementsByTagName("topology")[0].getAttribute("name")
h6=[]
for l in open(direct+name+"rtth3").xreadlines():
	fields = l.strip().split(':')
#	print fields
	h6.append(float(fields[1])/2)

h7=[]
for l in open(direct+name+"rtth4").xreadlines():
	fields = l.strip().split(':')
#	print fields
	h7.append(float(fields[1])/2)

	
N6 = len(h6)
ind6 = np.arange(N6)

N7 = len(h7)
ind7 = np.arange(N7)


#print cwnd

g = lambda x: 320 * 2
h = [g(x) for x in ind6]

fig = plt.figure()
axes = plt.gca()
#~ axes.set_xlim([xmin,xmax])
#	axes.set_ylim([14.4,14.5])
#~ axes.set_xlim([0,N1])
ax = fig.add_subplot(111)
plt1,=ax.plot(ind6/2+10,h6,label='flow 1')
plt2,=ax.plot(ind7/2+100,h7,label='flow 2')
plt3,=ax.plot(ind6/2,h,label='ref')
plt.ylabel('rtt')
plt.xlabel('time(s)')
plt.legend(handles=[plt1,plt2])
fig.savefig(name+"-rtt.pdf")
