from scapy.all import *

TYPE_PROBE = 0x812

class Probe(Packet):
   fields_desc = [ ByteField("hop_cnt", 0),
   				   ByteField("type", 1)]


class ProbeDataQueue(Packet):
   fields_desc = [ BitField("bos", 0, 1),
                   BitField("swid", 0, 7),
                   IntField("queue_depth", 0)]

class ProbeDataLink(Packet):
   fields_desc = [ BitField("bos", 0, 1),
                   BitField("swid", 0, 7),
                   BitField("port", 0, 8),
                   IntField("byte_cnt", 0),
                   BitField("last_time", 0, 48),
                   BitField("cur_time", 0, 48)]


class ProbeDataTime(Packet):
   fields_desc = [ BitField("bos", 0, 1),
                   BitField("swid", 0, 7),
                   BitField("in_queue_time", 0, 32)]


class ProbeFwd(Packet):
   fields_desc = [ ByteField("egress_spec", 0)]

# Bind layers depending on its value
bind_layers(Ether, Probe, type=TYPE_PROBE)
# Count value = 0 means there are not hops
bind_layers(Probe, ProbeFwd, hop_cnt=0)
bind_layers(Probe, ProbeDataQueue, type=1)
bind_layers(Probe, ProbeDataLink, type=2)
bind_layers(Probe, ProbeDataTime, type=3)
# bind_layers(Probe, ProbeDataQueue, type=1)
# bind_layers(Probe, ProbeDataLink, type=2)
# bind_layers(Probe, ProbeDataTime, type=3)
# Depending on whether we are on last item of stack, bind probe data or final header
bind_layers(ProbeDataQueue, ProbeDataQueue, bos=0)
bind_layers(ProbeDataLink, ProbeDataLink, bos=0)
bind_layers(ProbeDataTime, ProbeDataTime, bos=0)
bind_layers(ProbeDataQueue, ProbeFwd, bos=1)
bind_layers(ProbeDataLink, ProbeFwd, bos=1)
bind_layers(ProbeDataTime, ProbeFwd, bos=1)
# There could be more stack of egress ports. Bind if any.
bind_layers(ProbeFwd, ProbeFwd)