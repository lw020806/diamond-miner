from ipaddress import IPv6Address

from diamond_miner.simulator.models import Node, Probe, Protocol
from diamond_miner.simulator.simulator import Simulator


def test_simulator():
    A = Node(IPv6Address("::1"))
    B = Node(IPv6Address("::2"))
    C = Node(IPv6Address("::3"))
    D = Node(IPv6Address("::4"))
    E = Node(IPv6Address("::5"))
    links = [
        (Simulator.SOURCE_NODE, A),
        (Simulator.SOURCE_NODE, B),
        (A, C),
        (A, D),
        (B, C),
        (B, D),
        (C, E),
        (D, E),
    ]
    sim = Simulator(links)
    # Make sure that all the paths are reachable.
    # (A bad hashing function can cause some paths to be unreachable.)
    all_paths = {
        (Simulator.SOURCE_NODE, A, C, E),
        (Simulator.SOURCE_NODE, A, D, E),
        (Simulator.SOURCE_NODE, B, C, E),
        (Simulator.SOURCE_NODE, B, D, E),
    }
    paths = set()
    for offset in range(255):
        probe = Probe(Protocol.icmp, IPv6Address("::1111:0") + offset, 24000, 33434, 32)
        paths.add(sim.path_for_probe(probe))
    assert paths == all_paths
