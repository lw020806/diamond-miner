from dataclasses import dataclass
from enum import Enum
from ipaddress import IPv6Address
from typing import List


class Protocol(Enum):
    icmp = 1
    icmp6 = 58
    udp = 17


@dataclass(frozen=True)
class Probe:
    protocol: Protocol
    dst_addr: IPv6Address
    src_port: int
    dst_port: int
    ttl: int

    @property
    def ipv6(self) -> bool:
        return not self.dst_addr.ipv4_mapped


@dataclass(frozen=True)
class Reply:
    probe_protocol: Protocol
    probe_src_addr: IPv6Address
    probe_dst_addr: IPv6Address
    probe_src_port: int
    probe_dst_port: int
    probe_ttl: int
    quoted_ttl: int
    reply_protocol: Protocol
    reply_src_addr: IPv6Address
    reply_icmp_type: int
    reply_icmp_code: int
    reply_ttl: int
    reply_size: int
    reply_mpls_labels: List[int]
    rtt: float


@dataclass(frozen=True)
class Node:
    address: IPv6Address
    reply_probability: float = 1.0
    load_balancing_strategy: str = "per_flow_hash"

    def flow_id(self, probe: Probe) -> int:
        if self.load_balancing_strategy == "per_flow_hash":
            return hash(
                (
                    self.address,
                    probe.protocol,
                    probe.dst_addr,
                    probe.src_port,
                    probe.dst_port,
                )
            )
        raise NotImplementedError
