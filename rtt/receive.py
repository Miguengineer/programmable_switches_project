#!/usr/bin/env python

from probe_hdrs import *
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
import sys

def expand(x):
    yield x
    while x.payload:
        x = x.payload
        yield x

packet_received = 0
# x and y data for RTT
x = np.linspace(0, 1000, num=1000)
y = np.zeros(1000)
# To update graph and not open a new window
plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)
line1,  = ax.plot(x, y, 'r-') 
plt.title('RTT using probe packets')
plt.ylim((0, 200))
plt.xlim((0, 400))
plt.xlabel('Packet number')
plt.ylabel('RTT (ms)')



def handle_pkt(pkt):
    global packet_received, x, y, fig, ax, line1
    if ProbeData in pkt:
        data_layers = [l for l in expand(pkt) if l.name=='ProbeData']
        print("RTT Packet just received. Displaying info...")
        for sw in data_layers:
            print("The sender switch is: " + str(sw.swid))
            print("The packet left the switch at: "+ str(sw.egress_time / 1e6) + " [s]")
            print("The packet returned the switch at: " + str(sw.ingress_time / 1e6) + " [s]")
            print("RTT is: " + str((sw.ingress_time - sw.egress_time) / 1e3) + " [ms]")
            y[packet_received] = (sw.ingress_time - sw.egress_time) / 1e3
            packet_received += 1
            line1.set_ydata(y)
            fig.canvas.draw()
            fig.canvas.flush_events()
        



def main():
    iface = 'eth0'
    print ("sniffing on {}".format(iface))
    sniff(iface = iface,
          prn = lambda x: handle_pkt(x))
    # Set up plot to call animate() function periodically


if __name__ == '__main__':
    main()
