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
plt.title('Time in Queue for Switch 1')
plt.ylim((0, 10))
plt.xlim((0, 400))
plt.xlabel('Packet number')
plt.ylabel('Time in Queue (ms)')



def handle_pkt(pkt):
    global packet_received, x, y, fig, ax, line1
    print ("Probe packed received. Displaying info...")
    if ProbeData in pkt:
        data_layers = [l for l in expand(pkt) if l.name=='ProbeData']
        switches_ids = []
        time_in_queue = []
        print ("")
        
        for sw in data_layers:
            switches_ids.append(sw.swid)
            time_in_queue.append(sw.queue_time / 1e3)
        switches_ids.reverse()
        time_in_queue.reverse()
        print ("The packet's route is: ")
        route = ""
        # Concatenate the packet's route
        for sw_id in switches_ids:
            route += "Switch " + str(sw_id) + "->"
        # Delete last arrow
        route = route[:len(route) - 2]
        print (route)
        print ("Reporting Time in Queue for each switch... ")
        for sw_idx in range(len(time_in_queue)):
            print ("Switch " + str(switches_ids[sw_idx]) + " has a time in queue of " + str(time_in_queue[sw_idx]) + "[ms]")
            if switches_ids[sw_idx] == 1 and packet_received < 1000:
                y[packet_received] = time_in_queue[sw_idx]
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
