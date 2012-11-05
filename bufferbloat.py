#!/usr/bin/python

"CS144 In-class exercise: Buffer Bloat"

from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser

import sys
import os

# Parse arguments

parser = ArgumentParser(description="Buffer sizing tests")
parser.add_argument('--bw-host', '-B',
                    dest="bw_host",
                    type=float,
                    action="store",
                    help="Bandwidth of host links",
                    required=True)

parser.add_argument('--bw-net', '-b',
                    dest="bw_net",
                    type=float,
                    action="store",
                    help="Bandwidth of network link",
                    required=True)

parser.add_argument('--delay',
                    dest="delay",
                    type=float,
                    help="Delay in milliseconds of host links",
                    default=10)

parser.add_argument('--dir', '-d',
                    dest="dir",
                    action="store",
                    help="Directory to store outputs",
                    default="results",
                    required=True)

parser.add_argument('-n',
                    dest="n",
                    type=int,
                    action="store",
                    help="Number of nodes in star.",
                    required=True)

parser.add_argument('--nflows',
                    dest="nflows",
                    action="store",
                    type=int,
                    help="Number of flows per host (for TCP)",
                    required=True)

parser.add_argument('--maxq',
                    dest="maxq",
                    action="store",
                    help="Max buffer size of network interface in packets",
                    default=1000)

parser.add_argument('--cong',
                    dest="cong",
                    help="Congestion control algorithm to use",
                    default="bic")

# Expt parameters
args = parser.parse_args()


class StarTopo(Topo):
    "Star topology for Buffer Sizing experiment"

    def __init__(self, n=2, cpu=None, bw_host=1000, bw_net=10,
                 delay=10, maxq=None):
        # Add default members to class.
        super(StarTopo, self ).__init__()

        # Create switch and host nodes
        for i in xrange(n):
            self.add_node( 'h%d' % (i+1), cpu=cpu )

        self.add_switch('s0', fail_mode='open')

        self.add_link('h1', 's0', bw=bw_net,
                      max_queue_size=int(maxq) )

        for i in xrange(1, n):
            self.add_link('h%d' % (i+1), 's0',
                          bw=bw_host, delay=delay )

def ping_latency(net):
    "(Incomplete) verify link latency"
    h1 = net.getNodeByName('h1')
    h1.sendCmd('ping -c 2 10.0.0.2')
    result = h1.waitOutput()
    print "Ping result:"
    print result.strip()


def bbnet():
    "Create network and run Buffer Bloat experiment"
    print "starting mininet ...."
    # Seconds to run iperf; keep this very high
    seconds = 3600
    start = time()
    # Reset to known state
    topo = StarTopo(n=args.n, bw_host=args.bw_host,
                    delay='%sms' % args.delay,
                    bw_net=args.bw_net, maxq=args.maxq)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink,
                  autoPinCpus=True)
    net.start()
    dumpNodeConnections(net.hosts)
    net.pingAll()
    ping_latency(net)
    print "Initially, the delay between two hosts is around %dms" % (int(args.delay)*2) 
    h2 = net.getNodeByName('h2')
    h2.sendCmd('iperf -s -p 5001 &')
    h1 = net.getNodeByName('h1')
    h1.sendCmd('iperf -c 10.0.0.2 -p 5001 -t 3600 -i 1 > iperf-qsize%s.txt &' % args.maxq)
    print "Now, we started iperf between 10.0.0.1 <-> 10.0.0.2, try \'h1 ping h2\' and see what's the delay now."
    CLI( net )    

if __name__ == '__main__':
    bbnet()
