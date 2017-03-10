import matplotlib.pyplot as plt
import numpy as np
from pylab import plot, show, savefig, xlim, figure, \
                hold, ylim, legend, boxplot, setp, axes

    
directlist = ["iperf-bbr4h","iperf-cubic4h","iperf-bbr4h-100%","iperf-cubic4h-100%","iperf-bbr4h-20%","iperf-cubic4h-20%"]
protlist = ["bbr","cubic"]
band = "100mb"
namelist =["4h-100MB-40ms","4h-100MB-80ms","4h-100MB-160ms"]

data = {}
var = {}
bbr_var = ()
cubic_var = ()
for i in range(0,len(directlist)):
	for k in range(0,len(namelist)):
		array=[]
		print i
		for l in open(directlist[i]+"/"+band+"/data/"+protlist[i%2]+"-"+namelist[k]+"-server-h1").xreadlines():
			
			if(l.find("bits/sec")>=0):
				fields = l.strip().split(' ')
				if(fields[-1] == "Kbits/sec"):
					array.append(float(fields[-2])*0.001)
				else:
					#print "mb"
					array.append(float(fields[-2]))
		data[i*3+k]=array
print data[2]
for j in range(0, len(data)):
	print np.var(data[j])
	var[j] = np.var(data[j])

print var



# function for setting the colors of the box plots pairs
def setBoxColors(bp):
    setp(bp['boxes'][0], color='blue')
    setp(bp['caps'][0], color='blue')
    setp(bp['caps'][1], color='blue')
    setp(bp['whiskers'][0], color='blue')
    setp(bp['whiskers'][1], color='blue')
    #setp(bp['fliers'][0], color='blue')
    #setp(bp['fliers'][1], color='blue')
    setp(bp['medians'][0], color='blue')

    setp(bp['boxes'][1], color='red')
    setp(bp['caps'][2], color='red')
    setp(bp['caps'][3], color='red')
    setp(bp['whiskers'][2], color='red')
    setp(bp['whiskers'][3], color='red')
    #setp(bp['fliers'][2], color='red')
    #setp(bp['fliers'][3], color='red')
    setp(bp['medians'][1], color='red')

# Some fake data to plot
A= [data[0],  data[3]]
B = [data[1], data[4]]
C = [data[2], data[5]]

#~ fig = figure()
#~ ax = axes()
#~ hold(True)

fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(6, 6), sharey=True)


def setPlots(ax, A, B, C, title):
	fs = 30
	# first boxplot pair
	bp = ax.boxplot(A, positions = [1, 2], widths = 0.6, showfliers=False)
	setBoxColors(bp)

	# second boxplot pair
	bp = ax.boxplot(B, positions = [3, 4], widths = 0.6, showfliers=False)
	setBoxColors(bp)

	# thrid boxplot pair
	bp = ax.boxplot(C, positions = [5, 6], widths = 0.6, showfliers=False)
	setBoxColors(bp)

	# set axes limits and labels
	ax.set_xlim(0.5,7)
	ax.set_ylim(-20,160)
	#ax.set_ylabel("Bandwidth (Mbps)",fontsize=40)
	ax.set_title(title, fontsize=fs)
	#ylim(-5,30)
	ax.set_xticklabels(['80', '160', '320'])
	ax.set_xticks([1.5, 3.5, 5.5])
	ax.tick_params(axis='x', labelsize=20)
	ax.tick_params(axis='y', labelsize=20)
	hB, = plot([1,1],'b-')
	hR, = plot([1,1],'r-')
	legend = ax.legend((hB, hR),('BBR', 'CUBIC'))
	legend.get_frame().set_linewidth(0.0)
	t1, t2 = legend.get_texts()
	t1.set_size('xx-large')
	t2.set_size('xx-large')
	hB.set_visible(False)
	hR.set_visible(False)
	return legend

legend1 = setPlots(axes[0],A,B,C, "large buffer")


A= [data[6],  data[9]]
B = [data[7], data[10]]
C = [data[8], data[11]]

setPlots(axes[1],A,B,C,"100% BDP")

A= [data[12],  data[15]]
B = [data[13], data[16]]
C = [data[14], data[17]]


setPlots(axes[2],A,B,C, "20% BDP")
# draw temporary red and blue lines and use them to create a legend
axes[2].set_xlabel("RTT (ms)",fontsize=40)
axes[1].set_ylabel("Bandwidth (Mbps)",fontsize=40)
fig.subplots_adjust(left=0.07,right=0.8,bottom=0.08,top=0.95,hspace=.4)
plt.yticks(range(0,160,50))
#~ savefig('boxcompare.png')
#~ show()
#~ plt.boxplot(data[0],positions = [1], widths = 0.6)
#~ plt.boxplot(data[1],positions = [2], widths = 0.6)
plt.show()


#~ N1 = len(data[servers[0]])
#~ ind1 = np.arange(N1)
#~ g = lambda x: (int(bw_d)/len(servers))
#~ fair = [g(x) for x in ind1]

#~ N = 3

#~ for i in range(0,len(var)/2):
	#~ bbr_var += (var[i],)
#~ #bbr_var = (20, 35, 30, 35, 27)
#~ #men_std = (2, 3, 4, 1, 2)

#~ ind = np.arange(N)  # the x locations for the groups
#~ width = 0.35       # the width of the bars

#~ fig, ax = plt.subplots()
#~ rects1 = ax.bar(ind, bbr_var, width, color='r')
#~ for i in range(len(var)/2,len(var)):
	#~ cubic_var += (var[i],)
#~ #cubic_var = (25, 32, 34, 20, 25)
#~ #women_std = (3, 5, 2, 3, 3)
#~ rects2 = ax.bar(ind + width, cubic_var, width, color='y')

#~ # add some text for labels, title and axes ticks
#~ ax.set_ylabel('Scores')
#~ ax.set_title('Scores by group and gender')
#~ ax.set_xticks(ind + width / 2)
#~ ax.set_xticklabels(('G1','G2','G3'))

#~ ax.legend((rects1[0], rects2[0]), ('BBR', 'CUBIC'))


#~ def autolabel(rects):
    #~ """
    #~ Attach a text label above each bar displaying its height
    #~ """
    #~ for rect in rects:
        #~ height = rect.get_height()
        #~ ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                #~ '%d' % int(height),
                #~ ha='center', va='bottom')

#~ autolabel(rects1)
#~ autolabel(rects2)

#~ plt.show()

#~ plts =[]
#~ i=1
#~ fig = plt.figure()
#~ axes = plt.gca()
#~ ax = fig.add_subplot(111)
#~ for h in servers:
	#~ N = len(data[h])
	#~ ind = np.arange(N)
	#~ delay = 0
	#~ for c in clients:
		#~ if clients[c][0] == h :
			#~ delay = clients[c][1]
	#~ plot,=ax.plot(2*ind+float(delay),data[h],label='flow'+str(i))
	#~ plts.append(plot)
	#~ i = i+1
	
#~ plt3,=ax.plot(2*ind1,fair,label='ref')
#~ plt.ylabel('Mbits/s')
#~ plt.xlabel('time(s)')
#~ plt.legend(handles=plts)
#~ fig.savefig(direct+"/plots/"+name+".pdf")

