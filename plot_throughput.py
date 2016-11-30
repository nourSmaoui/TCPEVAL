import matplotlib.pyplot as plt
import numpy as np
from xml.dom import minidom
from matplotlib.backends.backend_pdf import PdfPages

doc = minidom.parse("../TCPEVAL/bbr10h/bbr-10h-10MB-40ms.xml")
name = doc.getElementsByTagName("topology")[0].getAttribute("name")
h6=[]
for l in open("../TCPEVAL/bbr10h/"+name+"-server-h1").xreadlines():
#	print l.find("bits/sec")
	if(l.find("bits/sec")>=0):
		fields = l.strip().split(' ')
		if(fields[-1] == "Kbits/sec"):
			h6.append(float(fields[-2])*0.001)
		else:
			print "mb"
			h6.append(float(fields[-2]))
		

h7=[]
for l in open("../TCPEVAL/bbr10h/"+name+"-server-h2").xreadlines():
	if(l.find("bits/sec")>=0):
		fields = l.strip().split(' ')
		if(fields[-1] == "Kbits/sec"):
			h7.append(float(fields[-2])*0.001)
		else:
			h7.append(float(fields[-2]))
		print fields

	
N6 = len(h6)
ind6 = np.arange(N6)

N7 = len(h7)
ind7 = np.arange(N7)


#print cwnd


fig = plt.figure()
axes = plt.gca()
#~ axes.set_xlim([xmin,xmax])
#	axes.set_ylim([14.4,14.5])
#~ axes.set_xlim([0,N1])
g = lambda x: 5
h = [g(x) for x in ind6]
print h
ax = fig.add_subplot(111)
plt1,=ax.plot(2*ind6,h6,label='flow 1')
plt2,=ax.plot(2*ind7+100,h7,label='flow 2')
plt3,=ax.plot(2*ind6,h,label='ref')
plt.ylabel('Mbits/s')
plt.xlabel('time(s)')
plt.legend(handles=[plt1,plt2])
fig.savefig(name+".pdf")

