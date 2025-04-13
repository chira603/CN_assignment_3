# Computer Networks Assignment: Network Topology and Routing Algorithms

## 1. Overview

### Objective (Part 1)
Configure a network topology using Mininet with multiple switches and hosts; run ping tests between selected hosts; observe packet drops caused by layer 2 loops (e.g., broadcast storms and MAC table instability) and then resolve the issue by enabling Spanning Tree Protocol (STP) on the switches.

### Objective (Part 2)
Implement and analyze the Distance Vector Routing Algorithm on a simulated network. The simulation involves four nodes with asymmetric link costs to study how routing information is exchanged, how the network converges to the optimal routes, and the effects of dynamic link cost changes.

## 2. Setup and Requirements

### Software Requirements
- Mininet for network topology simulation
- OVS (Open vSwitch) for switch configurations
- Python (with appropriate libraries) to execute scripts and command tests

### System Requirements
- A Linux-based environment for running Mininet
- Sufficient privileges (sudo) to set up and modify network configurations

### Additional Tools
- Packet capture (e.g., Wireshark or tcpdump) for monitoring ARP broadcasts and other network traffic
- Image scanner or digital capture tools for incorporating test results into the report

## 3. Assignment Details

### 3.1 Question 1: Network Simulation in Mininet

#### 3.1.1 Topology Setup

**Network Design:**
- **Switches:** Four switches (s1, s2, s3, and s4) are created.
- **Hosts:** Eight hosts (h1 to h8) are assigned with specific IP addresses in the 10.0.0.0/24 subnet.

**Links:**
- Host-to-switch links are set up with a latency of 5ms.
- Switch-to-switch links are established with a latency of 7ms. Some redundant links (including diagonal links) introduce multiple active paths.

**Key Code Implementation:**
The provided script defines a custom topology and uses the TCLink class for setting specific delays, which is critical for simulating real-life latency and the network effects of broadcast storms.

#### 3.1.2 Testing Procedures

**Ping Tests:**

**Part a:**
- **Action:** Host h3 attempts to ping h1 three separate times for 30 seconds each.
- **Observation:** 100% packet loss was observed.
- **Documentation:** Outputs showing "ping -w 30" results with total packet loss.

**Part b:**
- **Action:** Host h5 pings h7 three times with the same duration.
- **Observation:** Similar 100% packet loss observed.

**Part c:**
- **Action:** Host h8 pings h2 three times.
- **Observation:** Again, 100% packet loss was recorded.

#### 3.1.3 Analysis – Why the Pings Fail

**Identified Issues:**

1. **Layer 2 Loops:**
   The redundant switch-to-switch links cause loop formations in the network. Without a mechanism to avoid these loops, the network experiences multiple forwarding paths.

2. **Broadcast Storms:**
   ARP requests and broadcast frames are continuously forwarded in loops, leading to network saturation.

3. **MAC Table Instability:**
   The repetitive looping of identical packets prevents the switches from establishing correct and stable CAM table entries, leading to misrouted packets.

4. **Network Congestion:**
   The combination of loops, broadcast storms, and switch flooding results in significant congestion. Consequently, unicast traffic, such as ICMP (ping) packets, is dropped.

**Analysis Results:**
- ARP packet captures clearly demonstrate multiple ARP packets in circulation.
- The captured evidence highlights the overwhelming broadcast traffic prior to the introduction of STP.

#### 3.1.4 Resolution – Enabling STP

**Method:**
To resolve the issue, STP (Spanning Tree Protocol) was enabled on all switches via the following command:

```bash
for sw in ['s1', 's2', 's3', 's4']:
    sw_obj = net.get(sw)
    sw_obj.cmd('ovs-vsctl set Bridge {} stp_enable=true'.format(sw))
```

**Outcome:**
- Upon re-running the ping tests (h3 to h1, h5 to h7, and h8 to h2), the packet loss was eliminated.
- The network topology stabilized, and optimal paths were enforced automatically as STP disabled redundant links.

**Results Documentation:** 
The results after STP implementation show successful ping responses and a clean ARP packet capture, indicating improved network performance.

### 3.2 Question 2
*Note: Content for Question 2 will be provided when available.*

### 3.3 Question 3: Simulation and Analysis of the Distance Vector Routing Algorithm

#### 3.3.1 Introduction

**Objective:**
Implement and analyze the Distance Vector Routing Algorithm to understand the propagation of routing information in a distributed network setting.

#### 3.3.2 Network Topology and Initial Setup

**Nodes and Links:**
- Four nodes (labeled 0 to 3) are set up with asymmetric link costs.

**Example direct link costs:**
- Node 0: to Node 1 (cost 1), Node 2 (cost 3), Node 3 (cost 7)
- Node 1: to Node 0 (cost 1), Node 2 (cost 1)
- Node 2: to Node 0 (cost 3), Node 1 (cost 1), Node 3 (cost 2)
- Node 3: to Node 0 (cost 7), Node 2 (cost 2)

**Initialization:**
Each node initializes its distance table using the direct link costs and broadcasts its initial distance vector to its neighbors.

#### 3.3.3 Convergence Analysis

**Observation Rounds:**

**First Round (Time ~1.0 seconds):**
- Node 0 refines its route to Node 2 via Node 1.
- Node 3 finds a route to Node 1 via Node 2.
- Node 1 improves its route to Node 3 from a cost of 8 (via Node 0) to 3 (via Node 2).

**Second Round (Time ~2.0 seconds):**
- Node 0 updates the path to Node 3 via Node 2 (cost becomes 5).
- Node 3 reduces the cost to Node 0 via Node 2 (cost becomes 4).
- Further optimization leads to Node 0 achieving an even lower cost (4) to Node 3.

**Final Convergence (Time ~3.0 seconds):**
- All nodes reach optimal distance vectors.
- For example, Node 0's final distance vector becomes (0, 1, 2, 4).

#### 3.3.4 Link Cost Changes and Stability

**Simulated Dynamic Update:**
- At time 10000: An update between Node 0 and Node 1 was triggered, but with no effective cost change.
- At time 20000: Another update maintained the same cost.

**Outcome:**
The algorithm correctly identifies when link costs remain unchanged and avoids unnecessary updates, thereby preserving stability in the routing tables.

#### 3.3.5 Key Observations and Conclusion

**Rapid Convergence:**
The simulation demonstrated that the network quickly converges after a few rounds of updates.

**Path Optimization:**
Nodes discovered optimal paths (e.g., Node 0 routing to Node 3 via Nodes 1 and 2) that offered lower costs compared to direct links.

**Progressive Learning:**
The algorithm allows nodes to incrementally update their routing tables based on the information received from neighbors.

**Stability:**
Once the optimal routing table is established, the network remains stable unless there are actual link cost changes.

**Conclusion:**
The assignment effectively demonstrated the principles of the Distance Vector Routing Algorithm, including how nodes communicate, optimize routes, and maintain network stability through continual updates.

## 4. Execution Instructions

### Network Simulation (Question 1)

1. Ensure Mininet and OVS are installed on your Linux machine.

2. Run the topology script using the command:
   ```bash
   sudo python <script_name>.py
   ```

3. Monitor outputs in the terminal and use a packet capture tool (e.g., tcpdump) to validate ARP broadcasts and other traffic.

4. After capturing initial results (with packet loss), enable STP by executing the provided commands and re-run the tests to verify improvements.

### Distance Vector Routing Simulation (Question 3)

1. Compile the simulation code:
   ```bash
   gcc distance_vector.c node0.c node1.c node2.c node3.c create_rtpkt.c -o dvrouting
   ```

2. Execute the simulation:
   ```bash
   ./dvrouting 2
   ```

3. Observe the distance table convergence through printed output and debug logs.

4. Validate the simulation results with the provided analysis in the report.

