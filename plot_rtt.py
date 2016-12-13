import matplotlib.pyplot as plt
import numpy as np
from xml.dom import minidom
import sys

servers = []
dashservers = {}
clients = {}
dashclients = {}
iperf_e = False
dash_e = False


direct = sys.argv[1]
XML = sys.argv[2]

doc = minidom.parse(direct+"/"+XML)
name = doc.getElementsByTagName("topology")[0].getAttribute("name")

backbone_d = doc.getElementsByTagName("backbone")
bw_d = backbone_d[0].getElementsByTagName("bandwidth")[0].firstChild.data
delay_d = backbone_d[0].getElementsByTagName("delay")[0].firstChild.data

iperf_d = doc.getElementsByTagName("iperf")

if(iperf_d != []):
	iperf_e = True
	nodes_d = iperf_d[0].getElementsByTagName("node")
	for node in nodes_d:
		if node.getAttribute("type") == "server":
			servers.append(node.firstChild.data)
		else:
			clients[node.firstChild.data] = [node.getAttribute("server"),node.getAttribute("delay")]
			
dash_d = doc.getElementsByTagName("dash")

if(dash_d != []):
	dash_e = True
	nodes_d = dash_d[0].getElementsByTagName("node")
	for node in nodes_d:
		if node.getAttribute("type") == "server":
			dashservers[node.firstChild.data] = node.getAttribute("port")
		else:
			dashclients[node.firstChild.data] = [node.getAttribute("server"),node.getAttribute("delay")]
		
data = {}

if(iperf_e == True):

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

data = {}

if(dash_e == True):

	for h in dashservers.keys():
		array=[]
		for l in open(direct+"/data/"+name+"-dash-rtt"+h).xreadlines():
			if(l=="0\n"):
				array.append(0)
			else:
				fields = l.strip().split(':')
				array.append(float(fields[1])/2)
		data[h]=array

	N1 = len(data[dashservers.keys()[0]])
	ind1 = np.arange(N1)

	g = lambda x: int(delay_d) * 2
	rtt = [g(x) for x in ind1]

	i = 1
	plts =[]
	fig = plt.figure()
	axes = plt.gca()
	ax = fig.add_subplot(111)

	for h in dashservers.keys():
		N = len(data[h])
		ind = np.arange(N)
		plot,=ax.plot(ind/2,data[h],label='flow'+str(i))
		plts.append(plot)
		i = i+1
		
	plt3,=ax.plot(ind1/2,rtt,label='ref')
	plt.ylabel('rtt')
	plt.xlabel('time(s)')
	plt.legend(handles=plts)
	fig.savefig(direct+"/plots/"+name+"-dash-rtt.pdf")
