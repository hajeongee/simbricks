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

import simbricks.orchestration.experiments as exp
import simbricks.orchestration.nodeconfig as node
import simbricks.orchestration.simulators as sim

max_num_cpu = 24
# nums_of_cpus = [ i for i in range(1, max_num_cpu) ]
nums_of_cpus = [1, 4, 8, 12, 16, 20]
nums_of_numas = [2, 3, 4] # Min 2 NUMA node
experiments = []
for num_numas in nums_of_numas:
    for num_cpus in nums_of_cpus:

        e = exp.Experiment(
            'split-' +f'{num_numas}x' + f'{num_cpus}'
        )

        mem_sys = sim.Gem5Sysbus(node.NodeConfig)
        mem_sys.num_numa = num_numas
        #mem_sys.extra_main_args = ['--debug-flags=SplitCPUAdapter,SplitMEMAdapter,SimBricks']

        # Need to set how many cores per Node 
        # For sysbus calculating address range for per NUMA node
        mem_sys.num_core = num_cpus 
        e.add_splitsysbus(mem_sys)

        for i in range(num_numas):
            mem = sim.Gem5Mem(node.NodeConfig)
            mem.name += f'{i}'
            mem.is_one_numa = False
            mem.numa_idx = i
            mem.numa_num = num_numas
            mem.num_cpu = num_cpus
            mem_sys.add_mem(mem)
            #mem.extra_main_args = ['--debug-flags=SplitCPUAdapter,SplitMEMAdapter,SimBricks']
            e.add_splitmem(mem)

            for j in range(num_cpus):
                core_idx = i * num_cpus + j
                core = sim.Gem5Core(node.NodeConfig)
                core.name = f'{core_idx}'
                core.cpu_idx = core_idx
                core.add_mem(mem)
                #core.extra_main_args = ['--debug-flags=SplitCPUAdapter,SplitMEMAdapter,SimBricks']

                core.wait = True
                e.add_splitcore(core)

        experiments.append(e)