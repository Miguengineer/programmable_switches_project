from scapy.all import *

TYPE_PROBE = 0x812

class Probe(Packet):
   fields_desc = [ ByteField("hop_cnt", 0)]

class ProbeData(Packet):
   fields_desc = [ BitField("bos", 0, 1),
                   BitField("swid", 0, 7),
                   IntField("queue_time", 0)]

class ProbeFwd(Packet):
   fields_desc = [ ByteField("egress_spec", 0)]

# Bind layers depending on its value
bind_layers(Ether, Probe, type=TYPE_PROBE)
# Count value = 0 means there are not hops
bind_layers(Probe, ProbeFwd, hop_cnt=0)
bind_layers(Probe, ProbeData)
# Depending on whether we are on last item of stack, bind probe data or final header
bind_layers(ProbeData, ProbeData, bos=0)
bind_layers(ProbeData, ProbeFwd, bos=1)
# There could be more stack of egress ports. Bind if any.
bind_layers(ProbeFwd, ProbeFwd)