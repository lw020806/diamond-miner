import asyncio
import logging
import pickle
import random
import uuid
from dataclasses import asdict
from ipaddress import IPv6Address, IPv6Network
from typing import List, Optional, Tuple

from aioch import Client

from diamond_miner.database import create_tables, drop_tables, table_name
from diamond_miner.generator import probe_generator_by_flow
from diamond_miner.mappers import SequentialFlowMapper
from diamond_miner.queries import GetLinks, GetLinksFromView
from diamond_miner.rounds.mda import mda_probes
from diamond_miner.simulator.simulator import Node, Probe, Protocol, Reply, Simulator


def random_topology2(
    max_depth: int, max_width: int, seed: int
) -> List[Tuple[Node, Node]]:
    rng = random.Random(seed)
    # TODO: non fully connected, reply probability
    depth = rng.randint(2, max_depth)
    nodes = {0: [Simulator.SOURCE_NODE]}
    i = IPv6Address("::ffff:1.0.0.0")
    for ttl in range(1, depth):
        nodes[ttl] = []
        width = rng.randint(1, max_width)
        for node in range(width):
            nodes[ttl].append(Node(i))
            i += 1
    edges = set()
    for ttl in range(depth - 1):
        for near in nodes[ttl]:
            for far in nodes[ttl + 1]:
                edges.add((near, far))
    return list(edges)


def random_topology(destination_prefix: IPv6Network) -> List[Tuple[Node, Node]]:
    # TODO: Generate a random number of hosts in the destination prefix.
    A = Node(IPv6Address("::ffff:1.0.0.1"))
    B = Node(IPv6Address("::ffff:2.0.0.1"))
    C = Node(IPv6Address("::ffff:2.0.0.2"))
    D = Node(IPv6Address("::ffff:2.0.0.3"))
    E = Node(IPv6Address("::ffff:2.0.0.4"))
    F = Node(IPv6Address("::ffff:2.0.0.5"))
    G = Node(IPv6Address("::ffff:2.0.0.6"))
    H = Node(IPv6Address("::ffff:2.0.0.7"))
    Y = Node(IPv6Address("::ffff:3.0.0.1"))
    Z = Node(IPv6Address("::ffff:10.0.0.1"))
    return [
        (Simulator.SOURCE_NODE, A),
        (A, B),
        (A, C),
        (A, D),
        (A, E),
        (A, F),
        (A, G),
        (A, H),
        (B, Y),
        (C, Y),
        (D, Y),
        (E, Y),
        (F, Y),
        (G, Y),
        (H, Y),
        (Y, Z),
    ]


def to_ch(reply: Reply, round: int) -> dict:
    d = asdict(reply)
    d["probe_protocol"] = reply.probe_protocol.value
    d["reply_protocol"] = reply.reply_protocol.value
    d["round"] = round
    return d


async def insert(
    client: Client, suffix: str, replies: List[Optional[Reply]], round_: int
) -> None:
    sql = f"""
    INSERT INTO {table_name("results", suffix)} (
        probe_protocol,
        probe_src_addr,
        probe_dst_addr,
        probe_src_port,
        probe_dst_port,
        quoted_ttl,
        probe_ttl,
        reply_src_addr,
        reply_protocol,
        reply_icmp_type,
        reply_icmp_code,
        reply_ttl,
        reply_size,
        reply_mpls_labels,
        rtt,
        round
    )
    VALUES
    """
    await client.execute(sql, [to_ch(x, round_) for x in replies if x])

    sql = f"""
    INSERT INTO {table_name("links", suffix)}
    SELECT * FROM ({GetLinksFromView(round_eq=round_).query(table_name("flows", suffix))})
    """
    await client.execute(sql)


def make_probe(
    dst_addr: int, src_port: int, dst_port: int, ttl: int, protocol: str
) -> Probe:
    return Probe(Protocol[protocol], IPv6Address(dst_addr), src_port, dst_port, ttl)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    client = Client("127.0.0.1")
    suffix = f"__simulator__{uuid.uuid4()}"
    print(suffix)
    await drop_tables(client, suffix)
    await create_tables(client, suffix)

    sim = Simulator(random_topology2(8, 8, 2021))

    # Round 1
    gen = probe_generator_by_flow(
        prefixes=[("10.0.0.0/24", "icmp", range(1, 32))], flow_ids=range(1, 4096)
    )
    replies = [sim.simulate(make_probe(*probe)) for probe in gen]
    await insert(client, suffix, replies, 1)
    await asyncio.sleep(1)
    # TODO: Wait to make sure that the data is inserted?

    # Round 2+
    for round_ in range(1, 10):
        print(f"Round {round_} -> {round_ + 1}")
        mda_gen = mda_probes(
            client=client,
            table=table_name("links", suffix),
            round_=round_,
            mapper_v4=SequentialFlowMapper(),
            mapper_v6=SequentialFlowMapper(),
            probe_src_addr=str(Simulator.SOURCE_NODE.address),
            adaptive_eps=True,
        )
        stop = True
        replies = []
        async for probes in mda_gen:
            for probe in probes:
                replies.append(sim.simulate(make_probe(*probe)))
                stop = False
        await insert(client, suffix, replies, round_ + 1)
        await asyncio.sleep(1)
        if stop:
            print("Prefix resolved!")
            break

    links = await GetLinks(filter_partial=True, filter_virtual=True).execute_async(
        client, table_name("links", suffix)
    )
    sim_links = {
        (near.address, far.address)
        for near, far in sim.links
        if near != Simulator.SOURCE_NODE
    }
    inf_links = {x[0] for x in links}
    print(f"Simulator links: {len(sim_links)}")
    print(f"Inferred links: {len(inf_links)}")

    ghost = inf_links - sim_links
    missing = sim_links - inf_links
    print(f"Ghost links: {len(ghost)}")
    print(f"Missing links: {len(missing)}")

    if len(ghost) > 0 or len(missing) > 0:
        with open(f"{suffix}_sim_links.pkl", "wb") as f:
            pickle.dump(sim_links, f)
        with open(f"{suffix}_inf_links.pkl", "wb") as f:
            pickle.dump(inf_links, f)


if __name__ == "__main__":
    asyncio.run(main())
