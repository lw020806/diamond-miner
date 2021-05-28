from typing import List, Optional

import pytest
from aioch import Client

from diamond_miner.database import create_tables, drop_tables, table_name
from diamond_miner.generator import probe_generator_by_flow
from diamond_miner.mappers import RandomFlowMapper
from diamond_miner.queries import GetLinks, GetLinksFromView
from diamond_miner.rounds.mda import mda_probes
from diamond_miner.simulator.models import Probe, Reply
from diamond_miner.simulator.simulator import Simulator
from diamond_miner.simulator.topologies import fully_connected_topology


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
    await client.execute(sql, (x.to_row(round_) for x in replies if x))

    sql = f"""
    INSERT INTO {table_name("links", suffix)}
    SELECT * FROM ({GetLinksFromView(round_eq=round_).query(table_name("flows", suffix))})
    """
    await client.execute(sql)


@pytest.mark.asyncio
async def test_fully_connected(async_client):
    sim = Simulator(fully_connected_topology([8, 8, 32, 64, 32, 8]))

    suffix = "__test__fully_connected"
    await drop_tables(async_client, suffix)
    await create_tables(async_client, suffix)

    # Round 1
    gen = probe_generator_by_flow(
        prefixes=[("10.0.0.0/24", "icmp", range(1, 32))], flow_ids=range(1, 6)
    )
    replies = [sim.simulate(Probe.from_gen(*probe)) for probe in gen]
    await insert(async_client, suffix, replies, 1)

    # Round 2+
    for round_ in range(1, 10):
        mda_gen = mda_probes(
            client=async_client,
            table=table_name("links", suffix),
            round_=round_,
            mapper_v4=RandomFlowMapper(seed=2021),
            mapper_v6=RandomFlowMapper(seed=2021),
            probe_src_addr=str(Simulator.SOURCE_NODE.address),
            adaptive_eps=True,
        )
        replies = []
        stop = True
        async for probes in mda_gen:
            for probe in probes:
                replies.append(sim.simulate(Probe.from_gen(*probe)))
                stop = False
        await insert(async_client, suffix, replies, round_ + 1)
        if stop:
            break

    assert round_ < 10

    links = await GetLinks(filter_partial=True, filter_virtual=True).execute_async(
        async_client, table_name("links", suffix)
    )
    sim_links = {
        (near.address, far.address)
        for near, far in sim.links
        if near != Simulator.SOURCE_NODE
    }
    inf_links = {x[0] for x in links}
    print(f"Simulator links: {len(sim_links)}")
    print(f"Inferred links: {len(inf_links)}")

    sim_succ = {}
    for (near, far) in sim_links:
        sim_succ.setdefault(near, []).append(far)

    inf_succ = {}
    for (near, far) in inf_links:
        inf_succ.setdefault(near, []).append(far)

    fail = 0
    for sim_node in sim_succ:
        if len(sim_succ[sim_node]) != len(inf_succ[sim_node]):
            fail += 1
    print(fail / len(sim_succ) * 100)
