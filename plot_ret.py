import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
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
	with open(direct+"/data/"+name+"ret"+h, "r") as ins:
		for line in ins:
			try:
				array.append(int(line.split(' ')[4]))
			except:
				print "warning", line.split(' ')
	data[h]=array



fig = plt.figure()
axes = plt.gca()
ax = fig.add_subplot(111)
i = 1
plts = []

for h in clients.keys():
	N = len(data[h])
	ind = np.arange(N)
	plot,=ax.plot(ind/2,data[h],label='flow'+str(i))
	plts.append(plot)
	i = i+1



plt.ylabel('retransmissions')
plt.xlabel('time(s)')
plt.legend(handles=plts)
fig.savefig(direct+"/plots/"+name+"-ret.pdf")

