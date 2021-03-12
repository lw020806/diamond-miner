from ipaddress import ip_address

import pytest

from diamond_miner.generator import probe_generator
from diamond_miner.mappers import SequentialFlowMapper


@pytest.mark.asyncio
async def test_probe_generator_32():
    prefixes = ["8.8.8.8/32\n"]
    generator = probe_generator(
        prefixes=prefixes,
        prefix_len=32,
        min_flow=10,
        max_flow=12,
        min_ttl=41,
        max_ttl=42,
        mapper=SequentialFlowMapper(),
    )
    probes = [x async for x in generator]
    assert len(probes) == len(set(probes)) == 6
    for addr, src_port, dst_port, ttl in probes:
        assert addr == int(ip_address("8.8.8.8"))
        assert src_port in range(24010, 24013)
        assert dst_port == 33434
        assert ttl in range(41, 43)


@pytest.mark.asyncio
async def test_probe_generator_23():
    prefixes = ["0.0.0.0/23"]
    generator = probe_generator(
        prefixes=prefixes,
        prefix_len=24,
        min_flow=10,
        max_flow=10,
        min_ttl=41,
        max_ttl=41,
        mapper=SequentialFlowMapper(),
    )
    probes = [x async for x in generator]
    assert len(probes) == len(set(probes)) == 2
    for addr, src_port, dst_port, ttl in probes:
        assert addr in [int(ip_address("0.0.0.10")), int(ip_address("0.0.1.10"))]
        assert src_port == 24000
        assert dst_port == 33434
        assert ttl == 41
