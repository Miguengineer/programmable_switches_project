/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4  = 0x800;
const bit<16> TYPE_PROBE = 0x812;

#define MAX_HOPS 10
#define MAX_PORTS 8

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<32> q_depth;

typedef bit<32> time_t;
typedef bit<48> timestamp;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

// Top-level probe header, indicates how many hops this probe
// packet has traversed so far.
header probe_t {
    bit<8> hop_cnt;
    bit<8> type;
}


// The data added to the probe by each switch at each hop.
header probe_data_queue {
    bit<1>    bos; 
    bit<7>    swid;
    q_depth   queue_length;
}

header probe_data_link {
    bit<1>    bos;
    bit<7>    swid;
    bit<8>    port;
    bit<32>   byte_count;
    timestamp    last_time;
    timestamp    cur_time;
}

header probe_data_time {
    bit<1>   bos;
    bit<7>   swid;
    time_t   inqueue_time;
}

// Indicates the egress port the switch should send this probe
// packet out of. There is one of these headers for each hop.
header probe_fwd_t {
    bit<8>   egress_spec;
}

struct parser_metadata_t {
    bit<8>  remaining;
}

struct metadata {
    bit<8> egress_spec;
    parser_metadata_t parser_metadata;
}

struct headers {
    ethernet_t              ethernet;
    ipv4_t                  ipv4;
    probe_t                 probe;
    probe_data_queue[MAX_HOPS]  probe_data_q;
    probe_data_link[MAX_HOPS]   probe_data_l;
    probe_data_time[MAX_HOPS]   probe_data_t;
    probe_fwd_t[MAX_HOPS]   probe_fwd;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            TYPE_PROBE: parse_probe;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }
    
    
    // Parse probe data
    state parse_probe {
        packet.extract(hdr.probe);
        meta.parser_metadata.remaining = hdr.probe.hop_cnt + 1;
	// Depending on whether there is probe data, transition to ports or parse data.
        transition select(hdr.probe.hop_cnt) {
            0: parse_probe_fwd;
	    default: parse_aux;
        }	
    }
    // Auxiliar state to parse depending on the type of INT packet
    state parse_aux {
	transition select(hdr.probe.type){
	    1: parse_probe_queue;
	    2: parse_probe_link;
	    3: parse_probe_time;
	    default: accept;
	}

    }
    
    state parse_probe_queue {
	packet.extract(hdr.probe_data_q.next);
	transition select(hdr.probe_data_q.last.bos){
	    1: parse_probe_fwd;
	    default: parse_probe_queue;
	}
    }

    state parse_probe_link {
	packet.extract(hdr.probe_data_l.next);
	transition select(hdr.probe_data_l.last.bos) {
	    1: parse_probe_fwd;
	    default: parse_probe_link;
	}
    }

    state parse_probe_time {
	packet.extract(hdr.probe_data_t.next);
	transition select(hdr.probe_data_t.last.bos){
	    1: parse_probe_fwd;
	    default: parse_probe_time; 
	}
    }
    

    
    // Parse headers containing output ports
    state parse_probe_fwd {
        packet.extract(hdr.probe_fwd.next);
        meta.parser_metadata.remaining = meta.parser_metadata.remaining - 1;
        // extract the forwarding data. Last is the current element. So first port from left to right
        meta.egress_spec = hdr.probe_fwd.last.egress_spec;
        transition select(meta.parser_metadata.remaining) {
            0: accept;
            default: parse_probe_fwd;
        }
    }
}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    action drop() {
        mark_to_drop(standard_metadata);
    }
    
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }
    
    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }
    
    apply {
        if (hdr.ipv4.isValid()) {
            ipv4_lpm.apply();
        }
        else if (hdr.probe.isValid()) {
            standard_metadata.egress_spec = (bit<9>)meta.egress_spec;
            hdr.probe.hop_cnt = hdr.probe.hop_cnt + 1;
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   ********************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
    inout standard_metadata_t standard_metadata) {


    // Number of bytes since last probe
    register<bit<32>>(MAX_PORTS) byte_cnt_reg;
    // Last time a probe passed by this switch
    register<timestamp>(MAX_PORTS) last_time_reg;

    action set_swid_queue(bit<7> swid) {
	// Write this switch id to header
        hdr.probe_data_q[0].swid = swid;
	// Write queue depth that this packet experienced
	hdr.probe_data_q[0].queue_length = (q_depth) ((standard_metadata.deq_qdepth*100) >> 6);
    }

    action set_swid_link(bit<7> swid){
	hdr.probe_data_l[0].swid = swid;
    }

    action set_swid_time(bit<7> swid){
	hdr.probe_data_t[0].swid = swid;
	hdr.probe_data_t[0].inqueue_time = (time_t) standard_metadata.deq_timedelta;
    }

    table swid_queue {
        actions = {
            set_swid_queue;
            NoAction;
        }
        default_action = NoAction();
    }

    table swid_link {
	 actions = {
		set_swid_link;
		NoAction;
	    }
	    default_action = NoAction();
	    
	}
	table swid_time {
	    actions = {
		set_swid_time;
		NoAction;
	    }
	    default_action = NoAction();
	}
    

    apply {

	bit<32> byte_cnt;
	bit<32> new_byte_cnt;
	timestamp last_time;
	timestamp cur_time = standard_metadata.egress_global_timestamp;
	// Increment byte count for current port
	byte_cnt_reg.read(byte_cnt, (bit<32>)standard_metadata.egress_port);
	byte_cnt = byte_cnt + standard_metadata.packet_length;
	// Reset byte count if current packet is a probe packet
	if (hdr.probe.isValid()){
	    if (hdr.probe.type == 2){
		new_byte_cnt = 0;
	    }
	}
	else{
	    new_byte_cnt = byte_cnt;
	}
	// Write register with new byte count
	byte_cnt_reg.write((bit<32>)standard_metadata.egress_port, new_byte_cnt);
	
        if (hdr.probe.isValid()) {
            // Add info depending on type of header
	    if (hdr.probe.type == 1) {
		    hdr.probe_data_q.push_front(1);
		    hdr.probe_data_q[0].setValid();
		    if (hdr.probe.hop_cnt == 1){
			hdr.probe_data_q[0].bos = 1;
		    }
		    else{
			hdr.probe_data_q[0].bos = 0;
		    }
		    swid_queue.apply();
	    }
		else if (hdr.probe.type == 2){
		    hdr.probe_data_l.push_front(1);
		    hdr.probe_data_l[0].setValid();
		    if (hdr.probe.hop_cnt == 1){
			hdr.probe_data_l[0].bos = 1;
		    }
		    else{
			hdr.probe_data_l[0].bos = 0;
		    }
		swid_link.apply();
		hdr.probe_data_l[0].port = (bit<8>) standard_metadata.egress_port;
		hdr.probe_data_l[0].byte_count = byte_cnt;
		// Read register of last time access
		last_time_reg.read(last_time, (bit<32>)standard_metadata.egress_port);
		last_time_reg.write((bit<32>)standard_metadata.egress_port, cur_time);
		hdr.probe_data_l[0].last_time = last_time;
		hdr.probe_data_l[0].cur_time = cur_time;
		}
		else if (hdr.probe.type == 3) {
		    hdr.probe_data_t.push_front(1);
		    hdr.probe_data_t[0].setValid();
		    if (hdr.probe.hop_cnt == 1){
			hdr.probe_data_t[0].bos = 1;
		    }
		    else{
			hdr.probe_data_t[0].bos = 0;
		    }
		swid_time.apply();
		
		}	    
        }
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   ***************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
	      hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.probe);
        packet.emit(hdr.probe_data_q);
	packet.emit(hdr.probe_data_l);
	packet.emit(hdr.probe_data_t);
        packet.emit(hdr.probe_fwd);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
