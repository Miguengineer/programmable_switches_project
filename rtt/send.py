#!/usr/bin/env python
import sys
import time
from probe_hdrs import *

def main():

    probe_pkt = Ether(dst='ff:ff:ff:ff:ff:ff', src=get_if_hwaddr('eth0')) / \
                Probe(hop_cnt=0) / \
                ProbeData(swid=1) / \
                ProbeFwd(egress_spec=3) / \
                ProbeFwd(egress_spec=3) / \
                ProbeFwd(egress_spec=2)

    while True:
        try:
            sendp(probe_pkt, iface='eth0')
            time.sleep(0.01)
        except KeyboardInterrupt:
            sys.exit()

if __name__ == '__main__':
    main()
