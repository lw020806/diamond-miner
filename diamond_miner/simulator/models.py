import hashlib
from dataclasses import asdict, dataclass
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

    @classmethod
    def from_gen(
        cls, dst_addr: int, src_port: int, dst_port: int, ttl: int, protocol: str
    ) -> "Probe":
        return cls(Protocol[protocol], IPv6Address(dst_addr), src_port, dst_port, ttl)

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

    def to_row(self, round_: int) -> dict:
        return {
            **asdict(self),
            "probe_protocol": self.probe_protocol.value,
            "reply_protocol": self.reply_protocol.value,
            "round": round_,
        }


@dataclass(frozen=True)
class Node:
    address: IPv6Address
    reply_probability: float = 1.0
    load_balancing_strategy: str = "per_flow_hash"

    def flow_id(self, probe: Probe) -> int:
        if self.load_balancing_strategy == "per_flow_hash":
            m = hashlib.sha256()
            m.update(
                self.address.packed
                + probe.protocol.value.to_bytes(1, "little")
                + probe.dst_addr.packed
                + probe.src_port.to_bytes(2, "little")
                + probe.dst_port.to_bytes(2, "little")
            )
            return int.from_bytes(m.digest(), "little")
        raise NotImplementedError
