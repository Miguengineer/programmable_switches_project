from scapy.all import *

TYPE_PROBE = 0x812

class Probe(Packet):
   fields_desc = [ ByteField("hop_cnt", 0)]

class ProbeData(Packet):
   fields_desc = [ BitField("swid", 0, 8),
                   BitField("egress_time", 0, 48),
                   BitField("ingress_time", 0, 48)]

class ProbeFwd(Packet):
   fields_desc = [ ByteField("egress_spec", 0)]

# Bind layers depending on its value
bind_layers(Ether, Probe, type=TYPE_PROBE)
# Count value = 0 means there are not hops
bind_layers(Probe, ProbeFwd, hop_cnt=0)
bind_layers(Probe, ProbeData)
bind_layers(ProbeData, ProbeFwd)
# There could be more stack of egress ports. Bind if any.
bind_layers(ProbeFwd, ProbeFwd)