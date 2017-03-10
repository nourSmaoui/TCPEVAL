from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI  
from xml.dom import minidom
from mininet.node import OVSController
import time
import os
from subprocess import Popen, PIPE 
import re  
import pdb
import sys                      

hosts = {}
nodes = {}
servers = []
dashservers = {}
clients = {}
dashclients = {}


class Dummynet( Topo ):

	def __init__( self ):
		"Create custom topo."
		

		
		# Initialize topology
		Topo.__init__( self )
		self.iperf_e = False
		self.dash_e = False
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
		
		
		#self.addLink(nodes[backbone_d[0].getAttribute("n1")],nodes[backbone_d[0].getAttribute("n2")],bw=int(bw_d),delay=delay_d+'ms',max_queue_size=round(int(bw_d)*int(delay_d)*0.034)) #20% BDP
		self.addLink(nodes[backbone_d[0].getAttribute("n1")],nodes[backbone_d[0].getAttribute("n2")],bw=int(bw_d),delay=delay_d+'ms',max_queue_size=round(int(bw_d)*int(delay_d)*0.17)) #100%BDp
		#self.addLink(nodes[backbone_d[0].getAttribute("n1")],nodes[backbone_d[0].getAttribute("n2")],bw=int(bw_d),delay=delay_d+'ms')
		
		
		iperf_d = doc.getElementsByTagName("iperf")
		
		if(iperf_d != []):
			self.iperf_e = True
			nodes_d = iperf_d[0].getElementsByTagName("node")
			for node in nodes_d:
				if node.getAttribute("type") == "server":
					servers.append(node.firstChild.data)
				else:
					clients[node.firstChild.data] = [node.getAttribute("server"),node.getAttribute("delay")]
					
		dash_d = doc.getElementsByTagName("dash")
		
		if(dash_d != []):
			self.dash_e = True
			nodes_d = dash_d[0].getElementsByTagName("node")
			for node in nodes_d:
				if node.getAttribute("type") == "server":
					dashservers[node.firstChild.data] = [node.getAttribute("port"),node.getAttribute("size")]
					
				else:
					dashclients[node.firstChild.data] = [node.getAttribute("server"),node.getAttribute("delay")]
		#pdb.set_trace()
		
	def startIperfServers(self,net):
		if(self.iperf_e == True):
			for i in servers:
				h = net.get(i)
				h.cmd('iperf -s -i2 -B '+h.IP()+' -p 10001 > '+self.prot+"/data/"+self.name+'-server-'+i+' &')
	def startDashServers(self,net):
		print "starting dash servers"
		print self.dash_e
		if(self.dash_e == True):
			for i in dashservers.keys():
				h = net.get(i)
				h.cmd('python -m SimpleHTTPServer '+ dashservers[i][0]+' '+self.name+'-dash-server-'+i+' &')
				print ("starting server" + str(i))
	
	def startIperfClients(self,net):
		if(self.iperf_e == True):
			for key in clients.keys():
				h = net.get(key)
				s = net.get(clients[key][0])
				if float(clients[key][1])>0:
					if(float(clients[key][1]) > 1):
						h.cmd('`sleep '+clients[key][1]+';echo New connection > /dev/kmsg;iperf -c '+s.IP()+' -p 10001 -t '+str(self.duration-int(clients[key][1]))+' > '+self.prot+"/data/"+self.name+'-client-'+key+'` &')
					else:
						h.cmd('`./delay '+clients[key][1]+';echo New connection > /dev/kmsg;iperf -c '+s.IP()+' -p 10001 -t '+str(self.duration-float(clients[key][1]))+' > '+self.prot+"/data/"+self.name+'-client-'+key+'` &')
				else:
					h.cmd('iperf -c '+s.IP()+' -p 10001 -t '+str(self.duration)+' > '+self.prot+"/data/"+self.name+'-client-'+key+' &')
				h.cmd('pidiperf'+key+'=$!')
				
	def startDashClients(self,net):
		if(self.dash_e == True):
			for key in dashclients.keys():
				h = net.get(key)
				s = net.get(dashclients[key][0])
				p = dashservers[dashclients[key][0]][0]
				size = dashservers[dashclients[key][0]][1]
				if int(dashclients[key][1])>0:
					h.cmd('`sleep '+dashclients[key][1]+';/usr/bin/MP4Client http://'+s.IP()+':'+p+'/BigBuckBunny/'+size+'sec/BigBuckBunny_'+size+'s_simple_2014_05_09.mpd` &')
				else:
					h.cmd('`/usr/bin/MP4Client http://'+s.IP()+':'+p+'/BigBuckBunny/'+size+'sec/BigBuckBunny_'+size+'s_simple_2014_05_09.mpd` &')
				
	
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
		if(self.iperf_e == True):
			files = {}
			for key in clients.keys():
				h = net.get(key)
				f = open(self.prot+"/data/"+self.name+"cwnd"+key, "w")
				st = open(self.prot+"/data/"+self.name+"ssthresh"+key, "w")
				rt = open(self.prot+"/data/"+self.name+"ret"+key, "w")
				rtt = open(self.prot+"/data/"+self.name+"rtt"+key, "w")
				files[key] =  [h,f,st,rt,rtt]
			return files
		return {}
		
	def initializeDashOutputFiles(self,net):
		if(self.dash_e == True):
			files = {}
			for key in dashservers.keys():
				h = net.get(key)
				f = open(self.prot+"/data/"+self.name+"-dash-cwnd"+key, "w")
				st = open(self.prot+"/data/"+self.name+"-dash-ssthresh"+key, "w")
				rt = open(self.prot+"/data/"+self.name+"-dash-ret"+key, "w")
				rtt = open(self.prot+"/data/"+self.name+"-dash-rtt"+key, "w")
				thr = open(self.prot+"/data/"+self.name+"-dash-thr"+key, "w")
				files[key] =  [h,f,st,rt,rtt,thr]
			return files
		return {}
		
def perfTest():
	"Create network and run simple performance test"
	topo = Dummynet()
	os.system("sudo sysctl -w net.ipv4.tcp_congestion_control="+topo.tcp)
	net = Mininet(topo=topo, link=TCLink, controller= OVSController)
	net.start()
	print "Dumping host connections"
	dumpNodeConnections(net.hosts)
	print "Testing network connectivity"
	net.pingAll()
	print "starting iperf servers"
	topo.startIperfServers(net)
	print "starting iperf clients"
	topo.startIperfClients(net)
	topo.startDashServers(net)
	print "starting dash clients"
	topo.startDashClients(net) 
	
	#CLI(net)                               
	i = 0
	files = topo.initializeOutputFiles(net)
	dashFiles = topo.initializeDashOutputFiles(net)
	p = re.compile('cwnd:\d+')
	p2 = re.compile('ssthresh:\d+')
	p3 = re.compile('rtt:\d+\.\d+')
	p4 = re.compile('send \d+\.\d+')
	cwnd_b = True
	init_time = int(time.time())
	current = init_time
	while ((current-init_time)<topo.duration):
		print ("time : "+str(current-init_time)+" s")
		#cwnd_b = False
		if(topo.iperf_e == True):
			for key in files.keys():
				result = files[key][0].cmd('ss -i | grep cwnd')
				cwnd = p.findall(result)
				try:
					files[key][1].write( cwnd[0]+"\n")
					cwnd = None
					cwnd_b = cwnd_b or True
				except:
					print "cwnd "+key+" empty"
					#cwnd_b = cwnd_b or False
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
		if(topo.dash_e == True):
			for key in dashFiles.keys():
				result = dashFiles[key][0].cmd('ss -i | grep cwnd')
				cwnd = p.findall(result)
				try:
					dashFiles[key][1].write( cwnd[0]+"\n")
					#cwnd = None
					#cwnd_b = cwnd_b or True
				except:
					print "cwnd "+key+" empty"
					dashFiles[key][1].write( "0\n")
					#cwnd_b = cwnd_b or False
				rtt = p3.findall(result)
				try:
					dashFiles[key][4].write( rtt[0]+"\n")
				except:
					print "rtt "+key+" empty"
					dashFiles[key][4].write( "0\n")
				thro = p4.findall(result)
				try:
					dashFiles[key][5].write( thro[0]+"\n")
				except:
					print "thro "+key+" empty"
					dashFiles[key][5].write("0\n")
				ret1 = dashFiles[key][0].cmd('netstat -s | grep retransmited')
				try:
					dashFiles[key][3].write( ret1+"\n")
					ret1 = None
				except:
					print "ret "+key+" empty"
		current = int(time.time())
		time.sleep(0.5)
		i=i+0.5
	
	net.stop()
    
if __name__ == '__main__':
	setLogLevel('info')
	perfTest()
