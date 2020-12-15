#!/usr/bin/env python

from probe_hdrs import *
import sys
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
def expand(x):
    yield x
    while x.payload:
        x = x.payload
        yield x
packet_received = 0
x = np.linspace(0, 1000, num=1000)
y =     np.zeros(1000)
#x = np.linspace(0, 6*np.pi, 100)
#y = np.sin(x)
plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)
line1,  = ax.plot(x, y, 'r-') # Returns a tuple of line objects, thus the comma
plt.title('Queue depth for Switch 1')
plt.ylim((0, 100))
plt.xlim((0, 1000))
plt.xlabel('Packet number')
plt.ylabel('Queue Depth (%)')



def handle_pkt(pkt):
    global packet_received, x, y, fig, ax, line1
    print ("Probe packed received. Displaying info...")
    if ProbeData in pkt:
        data_layers = [l for l in expand(pkt) if l.name=='ProbeData']
        switches_ids = []
        queues_depths = []
        print ("")
        
        for sw in data_layers:
            switches_ids.append(sw.swid)
            queues_depths.append(sw.queue_depth)
        switches_ids.reverse()
        queues_depths.reverse()
        print ("The packet's route is: ")
        route = ""
        # Concatenate the packet's route
        for sw_id in switches_ids:
            route += "Switch " + str(sw_id) + "->"
        # Delete last arrow
        route = route[:len(route) - 2]
        print (route)
        print ("Reporting queues' depths for each switch... ")
        for sw_idx in range(len(queues_depths)):
            print ("Switch " + str(switches_ids[sw_idx]) + " has a queue depth of " + str(queues_depths[sw_idx]))
            if switches_ids[sw_idx] == 1 and packet_received < 1000:
                y[packet_received] = queues_depths[sw_idx]
                print(packet_received)
                packet_received += 1
                line1.set_ydata(y)
                fig.canvas.draw()
                fig.canvas.flush_events()


        print ("End of probe packet data")
        






def main():
    iface = 'eth0'
    print ("sniffing on {}".format(iface))
    sniff(iface = iface,
          prn = lambda x: handle_pkt(x))
    # Set up plot to call animate() function periodically


if __name__ == '__main__':
    main()
