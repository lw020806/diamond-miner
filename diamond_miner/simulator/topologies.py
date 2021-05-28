from ipaddress import IPv6Address
from typing import List, Sequence, Tuple

from diamond_miner.simulator.models import Node
from diamond_miner.simulator.simulator import Simulator

# def random_topology(
#     max_depth: int, max_width: int, seed: int
# ) -> List[Tuple[Node, Node]]:
#     rng = random.Random(seed)
#     # TODO: non fully connected, reply probability
#     depth = rng.randint(2, max_depth - 1)
#     nodes = {0: [Simulator.SOURCE_NODE]}
#     i = IPv6Address("::ffff:1.0.0.0")
#     for ttl in range(1, depth):
#         nodes[ttl] = []
#         width = rng.randint(1, max_width)
#         for node in range(width):
#             nodes[ttl].append(Node(i))
#             i += 1
#     edges = set()
#     for ttl in range(depth - 1):
#         for near in nodes[ttl]:
#             for far in nodes[ttl + 1]:
#                 edges.add((near, far))
#     for near in nodes[depth - 1]:
#         edges.add((near, Node(IPv6Address("::dead:beef"))))
#     return sorted(list(edges), key=lambda x: x[0].address)


def fully_connected_topology(widths: Sequence[int]) -> List[Tuple[Node, Node]]:
    depth = len(widths)
    nodes = {0: [Simulator.SOURCE_NODE]}
    edges = set()
    i = IPv6Address("::ffff:1.0.0.0")
    for ttl, width in enumerate(widths, start=1):
        nodes[ttl] = []
        for _ in range(width):
            nodes[ttl].append(Node(i))
            i += 1
    for ttl in range(depth):
        for near in nodes[ttl]:
            for far in nodes[ttl + 1]:
                edges.add((near, far))
    return list(edges)
