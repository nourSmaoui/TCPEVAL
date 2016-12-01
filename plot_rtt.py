import matplotlib.pyplot as plt
import numpy as np
from xml.dom import minidom
import sys

servers = []
clients = {}
direct = sys.argv[1]
XML = sys.argv[2]

doc = minidom.parse(direct+"/"+XML)
name = doc.getElementsByTagName("topology")[0].getAttribute("name")

backbone_d = doc.getElementsByTagName("backbone")
bw_d = backbone_d[0].getElementsByTagName("bandwidth")[0].firstChild.data
delay_d = backbone_d[0].getElementsByTagName("delay")[0].firstChild.data

iperf_d = doc.getElementsByTagName("iperf")
		
nodes_d = iperf_d[0].getElementsByTagName("node")
for node in nodes_d:
	if node.getAttribute("type") == "server":
		servers.append(node.firstChild.data)
	else:
		clients[node.firstChild.data] = [node.getAttribute("server"),node.getAttribute("delay")]
		
data = {}

for h in clients.keys():
	array=[]
	for l in open(direct+"/data/"+name+"rtt"+h).xreadlines():
		fields = l.strip().split(':')
		array.append(float(fields[1])/2)
	data[h]=array

N1 = len(data[clients.keys()[0]])
ind1 = np.arange(N1)

g = lambda x: int(delay_d) * 2
rtt = [g(x) for x in ind1]

i = 1
plts =[]
fig = plt.figure()
axes = plt.gca()
ax = fig.add_subplot(111)

for h in clients.keys():
	N = len(data[h])
	ind = np.arange(N)
	delay = clients[h][1]
	plot,=ax.plot(ind/2+int(delay),data[h],label='flow'+str(i))
	plts.append(plot)
	i = i+1

plt3,=ax.plot(ind1/2,rtt,label='ref')
plt.ylabel('rtt')
plt.xlabel('time(s)')
plt.legend(handles=plts)
fig.savefig(direct+"/plots/"+name+"-rtt.pdf")
