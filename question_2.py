#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import time, os
from mininet.node import OVSController, OVSSwitch

class CustomRoutingTopoNAT(Topo):
    def build(self):
        # Create four switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Add hosts:
        # Internal hosts using a private subnet (10.1.1.0/24)
        h1 = self.addHost('h1', ip='10.1.1.2/24')
        h2 = self.addHost('h2', ip='10.1.1.3/24')
        # External hosts remain in the 10.0.0.0/24 subnet
        h3 = self.addHost('h3', ip='10.0.0.4/24')
        h4 = self.addHost('h4', ip='10.0.0.5/24')
        h5 = self.addHost('h5', ip='10.0.0.6/24')
        h6 = self.addHost('h6', ip='10.0.0.7/24')
        h7 = self.addHost('h7', ip='10.0.0.8/24')
        h8 = self.addHost('h8', ip='10.0.0.9/24')
        # NAT host H9:
        # Use a public IP that is in the same subnet as external hosts.
        h9 = self.addHost('h9', ip='172.16.10.10/24')

        # Connect external hosts as before:
        self.addLink(h3, s2, delay='5ms')
        self.addLink(h4, s2, delay='5ms')
        self.addLink(h5, s3, delay='5ms')
        self.addLink(h6, s3, delay='5ms')
        self.addLink(h7, s4, delay='5ms')
        self.addLink(h8, s4, delay='5ms')

        # Internal hosts (h1 and h2) are no longer attached directly to s1.
        # Instead, attach them to H9 (the NAT host) with a 5ms link.
        self.addLink(h9, s1, delay='5ms')
        self.addLink(h1, h9, delay='5ms')
        self.addLink(h2, h9, delay='5ms')
        # Connect H9 to s1 (public interface)

        # Inter-switch links remain unchanged.
        self.addLink(s1, s2, delay='7ms')
        self.addLink(s2, s3, delay='7ms')
        self.addLink(s3, s4, delay='7ms')
        self.addLink(s4, s1, delay='7ms')
        self.addLink(s1, s3, delay='7ms')
    
def configure_nat_bridge(net):
    h1 = net.get('h1')
    h2 = net.get('h2')
    h9 = net.get('h9')

    for i in range(3, 9):  # h3 to h8
        h = net.get(f'h{i}')
        h.cmd(f'ip route add default via 10.0.0.1')  # Pick any gateway in subnet

    h9.cmd("ip addr add 10.0.0.1/24 dev h9-eth0")  # Add a gateway IP

    for hname in ['h3', 'h4', 'h5', 'h6', 'h7', 'h8']:
        host = net.get(hname)
        host.cmd("ip route add default via 10.0.0.1")
    


    # Set up a bridge br0 inside h9
    h9.cmd("ip link add name br0 type bridge")
    h9.cmd("ip link set dev br0 up")

    # Add h9-eth1 and h9-eth2 to the bridge
    h9.cmd("ip link set dev h9-eth1 master br0")
    h9.cmd("ip link set dev h9-eth2 master br0")



    h9.cmd("ip addr add 10.1.1.1/24 dev br0")  # Internal IP
    h9.cmd("ip addr add 10.0.0.10/24 dev h9-eth0")  # Secondary IP (external subnet)

    # Set default route for h1 and h2 via h9 internal IP
    h1.cmd("ip route add default via 10.1.1.1")
    h2.cmd("ip route add default via 10.1.1.1")

    # Enable IP forwarding on H9
    h9.cmd("sysctl -w net.ipv4.ip_forward=1")

    # Setup NAT using iptables (masquerade)
    h9.cmd("iptables -t nat -F")
    h9.cmd("iptables -t nat -A POSTROUTING -s 10.1.1.0/24 -o h9-eth0 -j MASQUERADE")
    h9.cmd("iptables -A FORWARD -i h9-eth0 -o br0 -m state --state RELATED,ESTABLISHED -j ACCEPT")
    h9.cmd("iptables -A FORWARD -i br0 -o h9-eth0 -j ACCEPT")


def run():
    # os.system('mn -c')
    topo = CustomRoutingTopoNAT()
    net = Mininet(topo=topo, controller=OVSController, link=TCLink, switch=OVSSwitch)
    configure_nat_bridge(net)
    net.start()

    info("\n*** Enabling STP on all switches\n")
    for sw in ['s1', 's2', 's3', 's4']:
        sw_obj = net.get(sw)
        sw_obj.cmd("ovs-vsctl set Bridge {} stp_enable=true".format(sw))


    # No need for extra static ARP entries now since the public IP is in the same subnet.
    h1 = net.get('h1')
    h2 = net.get('h2')


    info("\nWaiting 30 seconds for NAT and STP convergence...\n")
    time.sleep(30)
    for i in range(1, 4):
        info("\n*** Running Ping Tests (for NAT connectivity)\n")
        info("\nTest a.i: h1 (internal) ping h5 (external)\n")
        print(h1.cmd("ping -w 30 %s" % net.get('h5').IP()))
        info("\nTest a.ii: h2 (internal) ping h3 (external)\n")
        print(h2.cmd("ping -w 30 %s" % net.get('h3').IP()))
        
        info("\nTest b.i: h8 (external) ping h1\n")
        print(net.get('h8').cmd("ping -w 30 %s" % net.get('h1').IP()))
        info("\nTest b.ii: h6 (external) ping NAT (10.0.0.10) for h2\n")
        print(net.get('h6').cmd("ping -w 30 %s" % net.get('h2').IP()))

    for i in range(1, 4):
        info(f"\n*** Iperf test (i), run {i} of 3: h1 server, h6 client (120s)\n")
        h1.cmd("pkill -f iperf3")
        net.get('h6').cmd("pkill -f iperf3")
        h1.cmd("iperf3 -s -p 5001 &")
        time.sleep(5)
        print(net.get('h6').cmd("iperf3 -c 10.1.1.2 -t 120 -p 5001"))

        info(f"\n*** Iperf test (ii), run {i} of 3: h8 server, h2 client (120s)\n")
        net.get('h8').cmd("pkill -f iperf3")
        h2.cmd("pkill -f iperf3")
        net.get('h8').cmd("iperf3 -s -p 5002 &")
        time.sleep(5)
        print(h2.cmd("iperf3 -c 10.0.0.9 -t 120 -p 5002"))
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
