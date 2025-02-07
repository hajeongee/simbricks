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

import os


class ExpEnv(object):
    """Manages the experiment environment."""

    def __init__(self, repo_path, workdir, cpdir):
        self.create_cp = False
        self.pcap_file = ''
        self.repodir = os.path.abspath(repo_path)
        self.workdir = os.path.abspath(workdir)
        self.cpdir = os.path.abspath(cpdir)
        self.shm_base = self.workdir
        self.qemu_img_path = f'{self.repodir}/sims/external/qemu/build/qemu-img'
        self.qemu_path = (
            f'{self.repodir}/sims/external/qemu/build/'
            'x86_64-softmmu/qemu-system-x86_64'
        )
        self.qemu_kernel_path = f'{self.repodir}/images/bzImage'
        self.gem5_py_path = (
            f'{self.repodir}/sims/external/gem5/configs/simbricks/simbricks.py'
        )
        self.gem5_kernel_path = f'{self.repodir}/images/vmlinux'

    def gem5_path(self, variant):
        return f'{self.repodir}/sims/external/gem5/build/X86/gem5.{variant}'

    def hdcopy_path(self, sim):
        return f'{self.workdir}/hdcopy.{sim.name}'

    def hd_path(self, hd_name):
        return f'{self.repodir}/images/output-{hd_name}/{hd_name}'

    def hd_raw_path(self, hd_name):
        return f'{self.repodir}/images/output-{hd_name}/{hd_name}.raw'

    def cfgtar_path(self, sim):
        return f'{self.workdir}/cfg.{sim.name}.tar'

    def dev_pci_path(self, sim):
        return f'{self.workdir}/dev.pci.{sim.name}'

    def dev_mem_path(self, sim):
        return f'{self.workdir}/dev.mem.{sim.name}'

    def nic_eth_path(self, sim):
        return f'{self.workdir}/nic.eth.{sim.name}'

    def dev_shm_path(self, sim):
        return f'{self.shm_base}/dev.shm.{sim.name}'

    def n2n_eth_path(self, sim_l, sim_c):
        return f'{self.workdir}/n2n.eth.{sim_l.name}.{sim_c.name}'

    def net2host_eth_path(self, sim_n, sim_h):
        return f'{self.workdir}/n2h.eth.{sim_n.name}.{sim_h.name}'

    def net2host_shm_path(self, sim_n, sim_h):
        return f'{self.workdir}/n2h.shm.{sim_n.name}.{sim_h.name}'

    def proxy_shm_path(self, sim):
        return f'{self.shm_base}/proxy.shm.{sim.name}'

    def gem5_outdir(self, sim):
        return f'{self.workdir}/gem5-out.{sim.name}'

    def gem5_cpdir(self, sim):
        return f'{self.cpdir}/gem5-cp.{sim.name}'
