# Computer Networks Assignment

## Overview
This repository contains the implementation of network topology simulations and routing algorithms for a computer networks assignment. The assignment consists of three questions addressing different networking concepts.

## Execution Instructions

### Question 1: Network Topology Simulation
This section implements a network topology using Mininet and examines network behavior with loop detection and spanning tree protocol.

**To execute the simulation:**
```bash
sudo python3 question_1.py
```

### Question 2: Network Analysis
This section focuses on network analysis techniques and implementations.

**To execute the analysis:**
```bash
sudo python3 question_2.py
```

### Question 3: Distance Vector Routing Simulation
This section implements and analyzes the Distance Vector Routing Algorithm on a simulated network with asymmetric link costs.

**To compile the simulation code:**
```bash
gcc distance_vector.c node0.c node1.c node2.c node3.c create_rtpkt.c -o dvrouting
```

**To execute the simulation:**
```bash
./dvrouting 2
```

**Analysis Procedure:**
1. Observe the distance table convergence through printed output and debug logs.
2. Validate the simulation results with the provided analysis in the report.

## Requirements
- Linux-based environment
- Mininet
- Python 3
- GCC Compiler
- Root/sudo privileges for network configuration

## Documentation
For detailed analysis and results, please refer to the accompanying report document.
