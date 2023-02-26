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

max_num_cpu = 30
nums_of_cpus = [ i for i in range(1, max_num_cpu) ]

experiments = []
for num_cpus in nums_of_cpus:

    e = exp.Experiment(
        'split-' + f'{num_cpus}'
    )

    mem = sim.Gem5Mem(node.NodeConfig)
    mem.extra_main_args = ['--debug-flags=SplitMEMAdapter,SimBricks']
    mem.num_cpu = num_cpus
    e.add_splitmem(mem)
    mem.wait = True

    cores = []
    for i in range(num_cpus):
        core = sim.Gem5Core(node.NodeConfig)
        core.extra_main_args = ['--debug-flags=SplitCPUAdapter,SimBricks']
        core.name = f'{i}'
        core.cpu_idx = i
        core.add_mem(mem)
        e.add_splitcore(core)
        cores.append(core)

    if (num_cpus == 2):
        cores[1].variant = 'debug'
        cores[1].debug = True
        cores[1].wait = True
    experiments.append(e)