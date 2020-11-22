import sys

def expand(x):
    yield x
    while x.payload:
        x = x.payload
        yield x

def handle_pkt(pkt):
    print "Probe packed received. Displaying info..."
    if ProbeData in pkt:
        data_layers = [l for l in expand(pkt) if l.name=='ProbeData']
        switches_ids = []
        queues_depths = []
        print ""
        
        for sw in data_layers:
            switches_ids.append(sw.swid)
            queues_depths.append(sw.queue_depth)
        switches_ids.reverse()
        queues_depths.reverse()
        print "The packet's route is: "
        route = ""
        # Concatenate the packet's route
        for sw_id in switches_ids:
            route += "Switch " + str(sw_id) + "->"
        # Delete last arrow
        route = route[:len(route) - 2]
        print route
        print "Reporting queues' depths for each switch... "
        for sw_idx in range(len(queues_depths)):
            print "Switch " + str(switches_ids[sw_idx]) + " has a queue depth of " + str(queues_depths[sw_idx])
        print "End of probe packet data"


def main():
    iface = 'eth0'
    print "sniffing on {}".format(iface)
    sniff(iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
