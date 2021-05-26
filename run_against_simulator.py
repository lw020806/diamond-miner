import asyncio
import logging
from dataclasses import asdict
from ipaddress import IPv6Address
from typing import List, Optional

from aioch import Client

from diamond_miner.generator import probe_generator_by_flow
from diamond_miner.mappers import SequentialFlowMapper
from diamond_miner.queries import (
    CreateFlowsView,
    CreateLinksTable,
    CreateResultsTable,
    GetLinksFromView,
)
from diamond_miner.rounds.mda import mda_probes
from diamond_miner.simulator import Node, Probe, Protocol, Reply, Simulator


def to_ch(reply: Reply, round: int) -> dict:
    d = asdict(reply)
    d["probe_protocol"] = reply.probe_protocol.value
    d["reply_protocol"] = reply.reply_protocol.value
    d["round"] = round
    return d


async def insert(client: Client, replies: List[Optional[Reply]], round: int) -> None:
    await CreateResultsTable().execute_async(client, "results_simulator_000")
    await CreateFlowsView(parent="results_simulator_000").execute_async(
        client, "flows_simulator_000"
    )
    await CreateLinksTable().execute_async(client, "links_simulator_000")

    await client.execute(
        """INSERT INTO results_simulator_000 (
    probe_src_addr,
    probe_dst_addr,
    probe_src_port,
    probe_dst_port,
    probe_ttl_l3,
    probe_ttl_l4,
    probe_protocol,
    reply_src_addr,
    reply_protocol,
    reply_icmp_type,
    reply_icmp_code,
    reply_ttl,
    reply_size,
    reply_mpls_labels,
    rtt,
    round
    ) VALUES""",
        [to_ch(x, round) for x in replies if x],
    )
    await client.execute(
        f"""
        INSERT INTO links_simulator_000
        SELECT * FROM ({GetLinksFromView(round_eq=round).query("flows_simulator_000")})
        """
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    client = Client("127.0.0.1")

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
    sim = Simulator(
        [
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
    )
    gen = probe_generator_by_flow(
        prefixes=[("10.0.0.0/24", "icmp", range(32))], flow_ids=range(1, 6)
    )
    replies = []
    for dst_addr, src_port, dst_port, ttl, protocol in gen:
        probe = Probe(
            Protocol[protocol], IPv6Address(dst_addr), src_port, dst_port, ttl
        )
        replies.append(sim.simulate(probe))

    await client.execute("DROP TABLE IF EXISTS results_simulator_000")
    await client.execute("DROP TABLE IF EXISTS flows_simulator_000")
    await client.execute("DROP TABLE IF EXISTS links_simulator_000")

    await insert(client, replies, 1)

    for round in range(1, 10):
        print(f"Round {round} -> {round + 1}")
        mda_gen = mda_probes(
            client,
            "links_simulator_000",
            round,
            SequentialFlowMapper(),
            SequentialFlowMapper(),
            str(Simulator.SOURCE_NODE.address),
        )
        stop = True
        replies = []
        async for probes in mda_gen:
            for dst_addr, src_port, dst_port, ttl, protocol in probes:
                stop = False
                probe = Probe(
                    Protocol[protocol], IPv6Address(dst_addr), src_port, dst_port, ttl
                )
                replies.append(sim.simulate(probe))
        await insert(client, replies, round + 1)
        if stop:
            print("Prefix resolved!")
            break


if __name__ == "__main__":
    asyncio.run(main())
