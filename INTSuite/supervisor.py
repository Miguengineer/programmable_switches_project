#!/usr/bin/env python
import sys
import time
from probe_hdrs import *

option = 0
rate = 0
route = 0
def greeting_option():
    global option, rate, route
    print('')
    print('======================================================================')
    print('                   INT Monitoring Suite                             ')
    print('======================================================================')
    print('Welcome to the INT Monitoring Suite')
    print('Please, choose the type of monitoring by typing the number according to the menu')
    print('1. Queue Depth monitor')
    print('2. Link State monitor')
    print('3. Time in Queue monitor')
    option = input('')
    option = int(option)
    string_options = ['Queue Depth', 'Link State', 'Time in Queue']
    # Make sure is a valid option
    while option < 1 or option > 3:
        print('Invalid option, please try again')
        print('1. Queue Depth monitor')
        print('2. Link State monitor')
        print('3. Time in Queue monitor')
        option = input('')
        option = int(option)
    print("Your have chosen to monitor " + string_options[int(option) - 1])
    rate = input("Please, choose the rate in seconds at which probe packets should be sent. Value must be greater than 0 and less than or equal 10 \n")
    rate = float(rate)
    while rate <= 0 or rate > 10:
        print('Invalid rate, please try again')
        rate = input('')
        rate = float(rate)
    print('Please, choose the route by which you want to send the packets.')
    print('1. S1 -> S2 -> Collector')
    print('2. S1 -> S3 -> S2 -> Collector')
    print('3. S1 -> S2 -> S3 -> S1 -> S2 -> Collector')
    route = input()
    route = int(route)
    while route < 1 or route > 3:
        print('Invalid option, please try again')
        route = input()
        route = int(route)



def main():
    # Promp the user to enter the options
    greeting_option()
    # Create a packet depending on the chosen option
    if option == 1:
        # Check route
        if route == 1:
            probe_pkt = Ether(dst='ff:ff:ff:ff:ff:ff', src=get_if_hwaddr('eth0')) / \
                        Probe(hop_cnt=0, type=1) / \
                        ProbeFwd(egress_spec=3) / \
                        ProbeFwd(egress_spec=1)
                        
        elif route == 2:
            probe_pkt = Ether(dst='ff:ff:ff:ff:ff:ff', src=get_if_hwaddr('eth0')) / \
                        Probe(hop_cnt=0, type=1) / \
                        ProbeFwd(egress_spec=4) / \
                        ProbeFwd(egress_spec=3) / \
                        ProbeFwd(egress_spec=1)
                        
        else:
            probe_pkt = Ether(dst='ff:ff:ff:ff:ff:ff', src=get_if_hwaddr('eth0')) / \
                        Probe(hop_cnt=0, type=1) / \
                        ProbeFwd(egress_spec=3) / \
                        ProbeFwd(egress_spec=4) / \
                        ProbeFwd(egress_spec=2) / \
                        ProbeFwd(egress_spec=3) / \
                        ProbeFwd(egress_spec=1)
                        
    elif option == 2:
        # Check route
        if route == 1:
            probe_pkt = Ether(dst='ff:ff:ff:ff:ff:ff', src=get_if_hwaddr('eth0')) / \
                        Probe(hop_cnt=0, type=2) / \
                        ProbeFwd(egress_spec=3) / \
                        ProbeFwd(egress_spec=1) 
        elif route == 2:
            probe_pkt = Ether(dst='ff:ff:ff:ff:ff:ff', src=get_if_hwaddr('eth0')) / \
                        Probe(hop_cnt=0, type=2) / \
                        ProbeFwd(egress_spec=4) / \
                        ProbeFwd(egress_spec=3) / \
                        ProbeFwd(egress_spec=1)
        else:
            probe_pkt = Ether(dst='ff:ff:ff:ff:ff:ff', src=get_if_hwaddr('eth0')) / \
                        Probe(hop_cnt=0, type=2) / \
                        ProbeFwd(egress_spec=3) / \
                        ProbeFwd(egress_spec=4) / \
                        ProbeFwd(egress_spec=2) / \
                        ProbeFwd(egress_spec=3) / \
                        ProbeFwd(egress_spec=1)
    else:
         # Check route
        if route == 1:
            probe_pkt = Ether(dst='ff:ff:ff:ff:ff:ff', src=get_if_hwaddr('eth0')) / \
                        Probe(hop_cnt=0, type=3) / \
                        ProbeFwd(egress_spec=3) / \
                        ProbeFwd(egress_spec=1)
       
        elif route == 2:
            probe_pkt = Ether(dst='ff:ff:ff:ff:ff:ff', src=get_if_hwaddr('eth0')) / \
                        Probe(hop_cnt=0, type=3) / \
                        ProbeFwd(egress_spec=4) / \
                        ProbeFwd(egress_spec=3) / \
                        ProbeFwd(egress_spec=1)
        else:
            probe_pkt = Ether(dst='ff:ff:ff:ff:ff:ff', src=get_if_hwaddr('eth0')) / \
                        Probe(hop_cnt=0, type=3) / \
                        ProbeFwd(egress_spec=3) / \
                        ProbeFwd(egress_spec=4) / \
                        ProbeFwd(egress_spec=2) / \
                        ProbeFwd(egress_spec=3) / \
                        ProbeFwd(egress_spec=1)


    while True:
        try:
            sendp(probe_pkt, iface='eth0')
            time.sleep(rate)
        except KeyboardInterrupt:
            sys.exit()

if __name__ == '__main__':
    main()
