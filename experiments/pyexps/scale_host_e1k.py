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

import typing as tp
import simbricks.orchestration.experiments as exp
import simbricks.orchestration.nodeconfig as node
import simbricks.orchestration.simulators as sim

host_pairs = [2]

experiments = []

for host_p in host_pairs:
    e = exp.Experiment(f'scale_host-{host_p}')
    e.checkpoint = False

    net = sim.SwitchNet()
    e.add_network(net)


    server_hosts: tp.List[sim.Gem5Host] = []
    client_hosts: tp.List[sim.Gem5Host] = []

    for i in range(0, host_p):
        node_config = node.E1000LinuxNode()
        node_config.prefix = 24
        node_config.nockp = True
        
        # server IP starts from 1
        ip = 1 + i
        node_config.ip = f'10.0.{int(ip / 256)}.{ip % 256}'
        node_config.app = node.IperfTCPServer()
        node_config.force_mac_addr = f'00:90:00:00:00:{ip}'

        host = sim.Gem5Host(node_config)
        host.cpu_freq = "2GHz"
        host.name = f'server.{i}'
        host.variant = 'opt'
        host.add_netdirect(net)

        e.add_host(host)

        server_hosts.append(host)

    for i in range(0, host_p):
        node_config = node.E1000LinuxNode()
        node_config.prefix = 24
        node_config.nockp = True

        # client IP starts from 16
        ip = 1 + host_p + i
        node_config.ip = f'10.0.{int(ip / 256)}.{ip % 256}'
        node_config.app = node.IperfTCPClient()
        node_config.force_mac_addr = f'00:90:00:00:00:{ip}'

        server_ip = 1 + i
        node_config.app.server_ip = f'10.0.{int(server_ip / 256)}.{server_ip % 256}'

        host = sim.Gem5Host(node_config)
        host.cpu_freq = "2GHz"
        host.name = f'client.{i}'
        host.variant = 'opt'
        host.add_netdirect(net)

        e.add_host(host)

        host.wait = True
        client_hosts.append(host)

    
    experiments.append(e)