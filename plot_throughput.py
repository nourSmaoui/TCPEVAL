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

	for h in servers:
		array=[]
		for l in open(direct+"/data/"+name+"-dash-thr"+h).xreadlines():
		#	print l.find("bits/sec")
			if(l.find("bits/sec")>=0):
				fields = l.strip().split(' ')
				if(fields[-1] == "Kbits/sec"):
					array.append(float(fields[-2])*0.001)
				else:
					#print "mb"
					array.append(float(fields[-2]))
		data[h]=array

	N1 = len(data[servers[0]])
	ind1 = np.arange(N1)
	g = lambda x: (int(bw_d)/len(servers))
	fair = [g(x) for x in ind1]

	plts =[]
	i=1
	fig = plt.figure()
	axes = plt.gca()
	ax = fig.add_subplot(111)
	for h in servers:
		N = len(data[h])
		ind = np.arange(N)
		delay = 0
		for c in clients:
			if clients[c][0] == h :
				delay = clients[c][1]
		plot,=ax.plot(2*ind+int(delay),data[h],label='flow'+str(i))
		plts.append(plot)
		i = i+1
		
	plt3,=ax.plot(2*ind1,fair,label='ref')
	plt.ylabel('Mbits/s')
	plt.xlabel('time(s)')
	plt.legend(handles=plts)
	fig.savefig(direct+"/plots/"+name+".pdf")

data = {}

if(dash_e == True):

	for h in dashservers.keys():
		array=[]
		for l in open(direct+"/data/"+name+"-dash-thr"+h).xreadlines():
			if(l=="0\n"):
				array.append(0)
			else:
				fields = l.strip().split(' ')
				array.append(float(fields[1]))
		data[h]=array
		
	N1 = len(data[dashservers.keys()[0]])
	ind1 = np.arange(N1)
	g = lambda x: (int(bw_d)/len(dashservers.keys()))
	fair = [g(x) for x in ind1]

	plts =[]
	i=1
	fig = plt.figure()
	axes = plt.gca()
	ax = fig.add_subplot(111)
	for h in dashservers.keys():
		N = len(data[h])
		ind = np.arange(N)
		plot,=ax.plot(ind/2,data[h],label='flow'+str(i))
		plts.append(plot)
		i = i+1
		
	plt3,=ax.plot(ind1/2,fair,label='ref')
	plt.ylabel('Mbits/s')
	plt.xlabel('time(s)')
	plt.legend(handles=plts)
	fig.savefig(direct+"/plots/"+name+"-dash-thr.pdf")

