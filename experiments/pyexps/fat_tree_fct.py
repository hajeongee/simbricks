# Copyright 2021 Max Planck Institute for Software Systems, and
# National University of Singapore
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import math
import random
import typing as tp
import simbricks.orchestration.experiments as exp
import simbricks.orchestration.nodeconfig as node
import simbricks.orchestration.simulators as sim

host_percentage = [10, 20, 30, 100]
k_value = 4
flow_size = 2
measuer_tput = True

# Fat Tree parameters derived from k_value. Not variables
num_spine_sw = (k_value / 2) * (k_value / 2)
num_pod = k_value
num_agg_sw = k_value / 2
racks_per_pod = k_value / 2 # num_tor_sw
# num_hosts_per_rack = k_value / 2
num_hosts_per_rack = 8
total_hosts = num_pod * racks_per_pod * num_hosts_per_rack

experiments = []

def hostID_to_IP(host_id: int, gate: bool = False) -> str:
    """
    Convert host ID to IP address.
    Hosts are numbered in a row-major order.
    The host_0 in the first rack_0 is 0, the host_0 in the rack_1 is 1, and so on.

    """
    total_num_tor = num_pod * racks_per_pod
    sub_net_num = int(host_id % total_num_tor)
    ip1 = 10
    ip2 = sub_net_num // 256
    ip3 = sub_net_num % 256
    ip4 = int(1 + num_agg_sw + (host_id // total_num_tor)) 

    if gate:
        return f'{ip1}.{ip2}.{ip3}.1'
    else:
        return f'{ip1}.{ip2}.{ip3}.{ip4}'


for host_p in host_percentage:
    e = exp.Experiment(f'FCT_FatTree-{k_value}_{host_p}')
    e.checkpoint = False

    net = sim.NS3FCTNet()
    net.measure_tput = measuer_tput
    net.opt = f'--k_value={k_value} --flow_size={flow_size} --detail_host_percent={host_p/100.0}'
    e.add_network(net)

    # Number of detailed hosts, round up to the nearest even number
    # For having a pair of server and client
    num_detail_hosts = round(total_hosts * host_p / 100.0)
    if num_detail_hosts == 0:
        num_detail_hosts = 0
    else:
        if num_detail_hosts % 2 != 0:
            num_detail_hosts += 1
    
    starting_host_idx = 0
    last_host_idx = total_hosts - 1

    print(f"detailed_percentage: {host_p}; num_detail_hosts: {num_detail_hosts}")

    server_hosts: tp.List[sim.Gem5Host] = []
    client_hosts: tp.List[sim.Gem5Host] = []

    num_pair = num_detail_hosts // 2
    
    for i in range(0, num_pair):
        
        # Create server hosts
        node_config = node.I40eLinuxNode()
        node_config.prefix = 24
        # node_config.nockp = True
        # server IP starts from 1
        server_node_id = int(starting_host_idx + i)
        server_ip = hostID_to_IP(server_node_id)
        gate_way_ip = hostID_to_IP(server_node_id, gate=True)
        node_config.ip = server_ip            
        node_config.app = node.FCTServer()
        node_config.app.gate_way_ip = gate_way_ip
        node_config.app.measure_tput = measuer_tput
        node_config.force_mac_addr = f'00:90:00:00:00:{server_node_id:02x}'

        host = sim.Gem5Host(node_config)
        host.cpu_freq = "5GHz"
        host.name = f'server.{i}'
        host.variant = 'fast'
        # host.cpu_type = 'X86KvmCPU'

        nic = sim.I40eNIC()
        e.add_nic(nic)
        host.add_nic(nic)
        nic.set_network(net)

        e.add_host(host)

        server_hosts.append(host) 

        print(f'server ID: {server_node_id} IP: {server_ip} MAC: {node_config.force_mac_addr}')

    for i in range(0, num_pair):

        # Create client hosts
        node_config = node.I40eLinuxNode()
        node_config.prefix = 24
        # node_config.nockp = True
        # client IP starts from 16
        server_node_id = int(starting_host_idx + i)
        server_ip = hostID_to_IP(server_node_id)
        client_node_id = int(total_hosts - server_node_id - 1)
        client_ip = hostID_to_IP(client_node_id)
        gate_way_ip = hostID_to_IP(client_node_id, gate=True)
        node_config.ip = client_ip
        node_config.app = node.FCTClient()
        node_config.app.measure_tput = measuer_tput
        node_config.app.rand_start = random.uniform(0, 0.002)
        node_config.app.gate_way_ip = gate_way_ip
        node_config.force_mac_addr = f'00:90:00:00:00:{client_node_id:02x}'

        # last client match to the first server
        print(f'host {client_node_id} client send to {server_node_id} server')
        node_config.app.server_ip = server_ip

        host = sim.Gem5Host(node_config)
        host.cpu_freq = "5GHz"
        host.name = f'client.{i}'
        host.variant = 'fast'
        # host.cpu_type = 'X86KvmCPU'

        nic = sim.I40eNIC()
        e.add_nic(nic)
        host.add_nic(nic)
        nic.set_network(net)

        e.add_host(host)
        
        # host.node_config.app.is_last = True
        
        client_hosts.append(host)
        print(f'client ID: {client_node_id} IP: {client_ip} MAC: {node_config.force_mac_addr}')
        print(f'send to server ID: {server_node_id} IP: {server_ip}')


    client_hosts[0].node_config.app.is_last = True
    client_hosts[0].wait = True

    
    experiments.append(e)


