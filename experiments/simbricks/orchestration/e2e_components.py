# Copyright 2023 Max Planck Institute for Software Systems, and
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

# Allow own class to be used as type for a method's argument
from __future__ import annotations

import typing as tp
from abc import ABC, abstractmethod

import sys


class E2EBase(ABC):

    def __init__(self) -> None:
        self.category: str
        self.mapping: tp.Dict[str, str] = {}
        self.components: tp.List[E2EComponent] = []

    def ns3_config(self) -> str:
        config_list = []
        for key, value in self.mapping.items():
            if value == "":
                continue
            config_list.append(f"{key}:{value}")
        config = ";".join(config_list)

        child_configs = " ".join([
            child.ns3_config() for child in self.components
        ])

        return f"--{self.category}={config} {child_configs}"

    @abstractmethod
    def add_component(self, component: E2EComponent) -> None:
        pass


class E2EGlobalConfig(E2EBase):

    def __init__(self) -> None:
        super().__init__()
        self.category = "Global"
        self.stop_time = ""

    def ns3_config(self) -> str:
        self.mapping.update({"StopTime": self.stop_time})
        return super().ns3_config()

    def add_component(self, component: E2EComponent) -> None:
        print("Can't add a component to the global config")
        sys.exit(1)


class E2EComponent(E2EBase):

    def __init__(self, idd: str) -> None:
        super().__init__()
        self.id = idd
        self.has_path = False
        self.type = ""

    def ns3_config(self) -> str:
        if self.id == "" or self.type == "":
            print("Id or Type cannot be empty")
            sys.exit(1)
        self.mapping.update({"Id": self.id, "Type": self.type})

        return super().ns3_config()

    def add_component(self, component: E2EComponent) -> None:
        self.components.append(component)

    def resolve_paths(self) -> None:
        self.has_path = True
        for component in self.components:
            if component.has_path:
                print(
                    f"Component {component.id} was already " +
                    "added to another component"
                )
                sys.exit(1)
            component.id = f"{self.id}/{component.id}"
            component.resolve_paths()


class E2ETopology(E2EComponent):

    def __init__(self, idd: str) -> None:
        super().__init__(idd)
        self.category = "Topology"


class E2EDumbbellTopology(E2ETopology):

    def __init__(self, idd: str) -> None:
        super().__init__(idd)
        self.type = "Dumbbell"
        self.data_rate = ""
        self.queue_size = ""
        self.delay = ""

    def ns3_config(self) -> str:
        self.mapping.update({
            "DataRate": self.data_rate,
            "QueueSize": self.queue_size,
            "Delay": self.delay,
        })
        return super().ns3_config()


class E2EHost(E2EComponent):

    def __init__(self, idd: str) -> None:
        super().__init__(idd)
        self.category = "Host"
        self.node_position = ""

    def ns3_config(self) -> str:
        self.mapping.update({"NodePosition": self.node_position})
        return super().ns3_config()


class E2ESimbricksHost(E2EHost):

    def __init__(self, idd: str) -> None:
        super().__init__(idd)
        self.type = "Simbricks"
        self.unix_socket = ""
        self.sync_delay = ""
        self.poll_delay = ""
        self.eth_latency = ""
        self.sync = True

        self.simbricks_host = None

    def ns3_config(self) -> str:
        self.mapping.update({
            "UnixSocket": self.unix_socket,
            "SyncDelay": self.sync_delay,
            "PollDelay": self.poll_delay,
            "EthLatency": self.eth_latency,
            "Sync": "1" if self.sync else "0",
        })
        return super().ns3_config()


class E2ESimpleNs3Host(E2EHost):

    def __init__(self, idd: str) -> None:
        super().__init__(idd)
        self.type = "SimpleNs3"
        self.data_rate = ""
        self.queue_size = ""
        self.delay = ""
        # todo change this to an enum
        self.congestion_control = ""
        self.ip = ""

    def ns3_config(self) -> str:
        self.mapping.update({
            "DataRate": self.data_rate,
            "QueueSize": self.queue_size,
            "Delay": self.delay,
            "CongestionControl": self.congestion_control,
            "Ip": self.ip,
        })
        return super().ns3_config()


class E2EApplication(E2EComponent):

    def __init__(self, idd: str) -> None:
        super().__init__(idd)
        self.category = "App"
        self.start_time = ""
        self.stop_time = ""

    def ns3_config(self) -> str:
        self.mapping.update({
            "StartTime": self.start_time,
            "StopTime": self.stop_time,
        })
        return super().ns3_config()


class E2EPacketSinkApplication(E2EApplication):

    def __init__(self, idd: str) -> None:
        super().__init__(idd)
        self.type = "PacketSink"
        self.protocol = "ns3::TcpSocketFactory"
        self.local_ip = ""

    def ns3_config(self) -> str:
        self.mapping.update({
            "Protocol": self.protocol,
            "Local": self.local_ip,
        })
        return super().ns3_config()


class E2EBulkSendApplication(E2EApplication):

    def __init__(self, idd: str) -> None:
        super().__init__(idd)
        self.type = "BulkSender"
        self.protocol = "ns3::TcpSocketFactory"
        self.remote_ip = ""

    def ns3_config(self) -> str:
        self.mapping.update({
            "Protocol": self.protocol,
            "Remote": self.remote_ip,
        })
        return super().ns3_config()


class E2EProbe(E2EComponent):

    def __init__(self, idd: str) -> None:
        super().__init__(idd)
        self.category = "Probe"


class E2EPeriodicSampleProbe(E2EProbe):

    def __init__(self, idd: str, probe_type: str) -> None:
        super().__init__(idd)
        self.type = probe_type
        self.file = ""
        self.header = ""
        self.unit = ""
        self.start = ""
        self.interval = ""

    def ns3_config(self) -> str:
        self.mapping.update({
            "File": self.file,
            "Header": self.header,
            "Unit": self.unit,
            "Start": self.start,
            "Interval": self.interval
        })
        return super().ns3_config()
