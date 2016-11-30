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
#		pdb.set_trace()
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
				
		# Add hosts and switches
		#~ h1 = self.addHost( 'h1' )
		#~ h2 = self.addHost( 'h2' )
		#~ h3 = self.addHost( 'h3' )
		#~ h4 = self.addHost( 'h4' )
		#~ h5 = self.addHost( 'h5' )
		#~ h6 = self.addHost( 'h6' )
		#~ s1 = self.addSwitch( 's1' )
		#~ s2 = self.addSwitch( 's2' )
		
		# Add links
		#self.addLink( leftHost, leftSwitch )
		#~ self.addLink( h1, s1 )
		#~ self.addLink( h2, s1 )
		#~ self.addLink( h5, s1 )
		#~ self.addLink( s1, s2, bw=5, delay='43ms' )
		#~ self.addLink( h3, s2 )
		#~ self.addLink( h4, s2 )
		#~ self.addLink( h6, s2 )
		#self.addLink( rightSwitch, rightHost )
		
	def startIperfServers(self,net):
		for i in servers:
			h = net.get(i)
			h.cmd('iperf -s -i2 -B '+h.IP()+' -p 10001 > '+self.prot+"/"+self.name+'-server-'+i+' &')
	
	def startIperfClients(self,net):
		for key in clients.keys():
			h = net.get(key)
			s = net.get(clients[key][0])
			if int(clients[key][1])>0:
				h.cmd('`sleep '+clients[key][1]+';iperf -c '+s.IP()+' -p 10001 -t '+str(self.duration-int(clients[key][1]))+' > '+self.prot+"/"+self.name+'-client-'+key+'` &')
			else:
				h.cmd('iperf -c '+s.IP()+' -p 10001 -t '+str(self.duration)+' > '+self.prot+"/"+self.name+'-client-'+key+' &')
			h.cmd('pidiperf'+key+'=$!')
	
	def isIperfOn(self,net):
		b= False
		for key in clients.keys():
			h = net.get(key)
			result = h.cmd('ps -aux | grep $pidiperf'+key+' | grep -v "grep"')
			b = b or result
		#~ result3 = h6.cmd('ps -aux | grep $pidh6 | grep -v "grep"')
		#~ if(result1 or result2 or result3):
		if(b):
			return True
		else:
			return False
			
	def initializeOutputFiles(self,net):
		files = {}
		for key in clients.keys():
			h = net.get(key)
			f = open(self.prot+"/"+self.name+"cwnd"+key, "w")
			st = open(self.prot+"/"+self.name+"ssthresh"+key, "w")
			rt = open(self.prot+"/"+self.name+"ret"+key, "w")
			rtt = open(self.prot+"/"+self.name+"rtt"+key, "w")
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
	print "Testing bandwidth between h1 and h4"
	#h1, h2, h3, h4 = net.get('h1','h2', 'h3', 'h4')
	#CLI(net)
#	net.iperf((h1, h4))
	#~ print "Inserting tcp probe"
#	start_tcpprobe()
#	h1.cmd('rmmod tcp_probe > /dev/null 2>&1;modprobe tcp_probe port=10001')
#	h2.cmd('rmmod tcp_probe > /dev/null 2>&1;modprobe tcp_probe port=10001')
	print "starting iperf servers"
	topo.startIperfServers(net)
	#~ h1.cmd('iperf -s -i2 -B 10.0.0.1 -p 10001 > server1 &')
	#~ h3.cmd('iperf -c 10.0.0.1 -p 10001 -t 1200 > client1 &')
	#~ h3.cmd('pidh3=$!')
#	CLI(net)
	#~ h2.cmd('iperf -s -i2 -B 10.0.0.2 -p 10001 > server2 &')
#	h5.cmd('iperf -s -i2 -B 10.0.0.5 -p 10001 > server5 &')
	print "outputting probe into files"
#	h1.cmd('cat /proc/net/tcpprobe > cwnd1 &')
#	h1.cmd('pid=$!')
#	h2.cmd('cat /proc/net/tcpprobe > cwnd2 &')
#	h2.cmd('pid=$!')
#	init1 = h1.cmd('netstat -s | grep retransmited') 
#	init2 = h2.cmd('netstat -s | grep retransmited')
	print "starting iperf clients"
	topo.startIperfClients(net) 
	
#	CLI(net)                               

	#~ h4.cmd('`sleep 100;iperf -c 10.0.0.2 -p 10001 -t 1100 > client2` &')
	#~ h4.cmd('pidh4=$!')
	#~ h6.cmd('iperf -c 10.0.0.5 -p 10001 -t 3600 > client6 &')
	#~ h6.cmd('pidh6=$!')
	i = 0
	files = topo.initializeOutputFiles(net)
	#~ f1 = open("cwnd1", "w")
	#~ st1 = open("ssthresh1", "w")
	#~ rt1 = open("ret1", "w")
	#~ f2 = open("cwnd2", "w")
	#~ rt2 = open("ret2", "w")
	#~ f3 = open("cwnd3", "w")
	p = re.compile('cwnd:\d+')
	p2 = re.compile('ssthresh:\d+')
	p3 = re.compile('rtt:\d+\.\d+')
	cwnd_b = True
	while (topo.isIperfOn(net) and cwnd_b):
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
		#~ ssthresh = p2.findall(result1)
		#~ try:
			#~ st1.write( ssthresh[0]+"\n")
			#~ ssthresh = None
		#~ except:
			#~ print "ssthresh[0] empty"
		#~ result2 = h4.cmd('ss -i | grep cwnd')
		#~ cwnd = p.findall(result2)
		#~ try:
			#~ f2.write( cwnd[0]+"\n")
			#~ cwnd = None
		#~ except:
			#~ print i,"cwnd2[0] empty"
		#~ ret2 = h4.cmd('netstat -s | grep retransmited')
		#~ try:
			#~ rt2.write( ret2+"\n")
			#~ ret2 = None
		#~ except:
			#~ print "ret2 empty" 
		#~ result3 = h6.cmd('ss -i | grep cwnd')
		#~ cwnd = p.findall(result3)
		#~ try:
			#~ f3.write( cwnd[0]+"\n")
		#~ except:
			#~ print "m[0] empty"
		time.sleep(0.5)
		i=i+1
	#~ f1.close()
	#~ f2.close()
	#~ st1.close()
	#~ rt1.close()
	#~ rt2.close()
	#~ f3.close()
	
	
#	end1 = h1.cmd('netstat -s | grep retransmited')    
#	end2 = h2.cmd('netstat -s | grep retransmited')  
	
#	print init1, end1
#	print init2, end2  
#	h1.cmd('ping -c4 '+ h4.IP())
#	print result

	
#	print "stopping tcp probe"
#	h1.cmd('kill $pid')
#	h2.cmd('kill $pid')
	net.stop()

#~ def isIperfOn(h3,h4):
	#~ result1 = h3.cmd('ps -aux | grep $pidh3 | grep -v "grep"')
	#~ result2 = h4.cmd('ps -aux | grep $pidh4 | grep -v "grep"')
	#~ if(result1 or result2):
		#~ return True
	#~ else:
		#~ return False


	
		
def start_tcpprobe():
    "Install tcp_pobe module and dump to file"
    os.system("(rmmod tcp_probe >/dev/null 2>&1); modprobe tcp_probe full=1")
    time.sleep(2)
    Popen("cat /proc/net/tcpprobe > ./dummynet_tcpprobe.txt", shell=True)
    
if __name__ == '__main__':
	setLogLevel('info')
	perfTest()
#topos = { 'Dummynet': ( lambda: Dummynet() ) }
