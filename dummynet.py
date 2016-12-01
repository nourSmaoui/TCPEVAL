from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI  
from xml.dom import minidom
import time
import os
from subprocess import Popen, PIPE 
import re  
import pdb
import sys                      

hosts = {}
nodes = {}
servers = []
clients = {}

class Dummynet( Topo ):

	def __init__( self ):
		"Create custom topo."
		

		
		# Initialize topology
		Topo.__init__( self )
		
		self.prot = sys.argv[1]
		self.XML = sys.argv[2]
		doc = minidom.parse(self.prot+"/"+self.XML)
		self.name = doc.getElementsByTagName("topology")[0].getAttribute("name")
		self.tcp = doc.getElementsByTagName("TCP-PROT")[0].firstChild.data
		hosts_d = doc.getElementsByTagName("host")
		
		self.duration = int(doc.getElementsByTagName("duration")[0].firstChild.data)
		
		for host in hosts_d:
			hosts[host.firstChild.data] = self.addHost(host.firstChild.data)
		
		switches_d = doc.getElementsByTagName("switch")
		
		for switch in switches_d:
			nodes[switch.firstChild.data] = self.addSwitch(switch.firstChild.data)
			
		links_d = doc.getElementsByTagName("link")
		
		for link in links_d:
			l1 = False
			l2 = False
			n1 = None
			n2 = None
			for key in hosts:
				if(key==link.getAttribute("n1") and l1 == False):
					l1=True
					n1 = hosts[link.getAttribute("n1")]
				if(key==link.getAttribute("n2") and l2 == False):
					l2=True
					n2 = hosts[link.getAttribute("n2")]
			for key in nodes:
				if(key==link.getAttribute("n1") and l1 == False):
					l1=True
					n1 = nodes[link.getAttribute("n1")]
				if(key==link.getAttribute("n2") and l2 == False):
					l2=True
					n2 = nodes[link.getAttribute("n2")]
					
			self.addLink(n1,n2)
		
		backbone_d = doc.getElementsByTagName("backbone")
		bw_d = backbone_d[0].getElementsByTagName("bandwidth")[0].firstChild.data
		delay_d = backbone_d[0].getElementsByTagName("delay")[0].firstChild.data
		
		
		self.addLink(nodes[backbone_d[0].getAttribute("n1")],nodes[backbone_d[0].getAttribute("n2")],bw=int(bw_d),delay=delay_d+'ms')
		
		
		iperf_d = doc.getElementsByTagName("iperf")
		
		nodes_d = iperf_d[0].getElementsByTagName("node")
		for node in nodes_d:
			if node.getAttribute("type") == "server":
				servers.append(node.firstChild.data)
			else:
				clients[node.firstChild.data] = [node.getAttribute("server"),node.getAttribute("delay")]
		
	def startIperfServers(self,net):
		for i in servers:
			h = net.get(i)
			h.cmd('iperf -s -i2 -B '+h.IP()+' -p 10001 > '+self.prot+"/data/"+self.name+'-server-'+i+' &')
	
	def startIperfClients(self,net):
		for key in clients.keys():
			h = net.get(key)
			s = net.get(clients[key][0])
			if int(clients[key][1])>0:
				h.cmd('`sleep '+clients[key][1]+';iperf -c '+s.IP()+' -p 10001 -t '+str(self.duration-int(clients[key][1]))+' > '+self.prot+"/data/"+self.name+'-client-'+key+'` &')
			else:
				h.cmd('iperf -c '+s.IP()+' -p 10001 -t '+str(self.duration)+' > '+self.prot+"/data/"+self.name+'-client-'+key+' &')
			h.cmd('pidiperf'+key+'=$!')
	
	def isIperfOn(self,net):
		b= False
		for key in clients.keys():
			h = net.get(key)
			result = h.cmd('ps -aux | grep $pidiperf'+key+' | grep -v "grep"')
			b = b or result
		if(b):
			return True
		else:
			return False
			
	def initializeOutputFiles(self,net):
		files = {}
		for key in clients.keys():
			h = net.get(key)
			f = open(self.prot+"/data/"+self.name+"cwnd"+key, "w")
			st = open(self.prot+"/data/"+self.name+"ssthresh"+key, "w")
			rt = open(self.prot+"/data/"+self.name+"ret"+key, "w")
			rtt = open(self.prot+"/data/"+self.name+"rtt"+key, "w")
			files[key] =  [h,f,st,rt,rtt]
		return files
		
def perfTest():
	"Create network and run simple performance test"
	topo = Dummynet()
	os.system("sudo sysctl -w net.ipv4.tcp_congestion_control="+topo.tcp)
	net = Mininet(topo=topo, link=TCLink)
	net.start()
	print "Dumping host connections"
	dumpNodeConnections(net.hosts)
	print "Testing network connectivity"
	net.pingAll()
	print "starting iperf servers"
	topo.startIperfServers(net)
	print "starting iperf clients"
	topo.startIperfClients(net) 
	
#	CLI(net)                               
	i = 0
	files = topo.initializeOutputFiles(net)
	p = re.compile('cwnd:\d+')
	p2 = re.compile('ssthresh:\d+')
	p3 = re.compile('rtt:\d+\.\d+')
	cwnd_b = True
	while (topo.isIperfOn(net) and cwnd_b):
		print ("time : "+str(i)+" s")
		cwnd_b = False
		for key in files.keys():
			result = files[key][0].cmd('ss -i | grep cwnd')
			cwnd = p.findall(result)
			try:
				files[key][1].write( cwnd[0]+"\n")
				cwnd = None
				cwnd_b = cwnd_b or True
			except:
				print "cwnd "+key+" empty"
				cwnd_b = cwnd_b or False
			rtt = p3.findall(result)
			try:
				files[key][4].write( rtt[0]+"\n")
			except:
				print "rtt "+key+" empty"
			ret1 = files[key][0].cmd('netstat -s | grep retransmited')
			try:
				files[key][3].write( ret1+"\n")
				ret1 = None
			except:
				print "ret "+key+" empty"
		time.sleep(0.5)
		i=i+0.5
	
	net.stop()
    
if __name__ == '__main__':
	setLogLevel('info')
	perfTest()
