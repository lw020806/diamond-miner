import pytest

from diamond_miner.generator import probe_generator
from diamond_miner.mappers import SequentialFlowMapper
from diamond_miner.utilities import format_ipv6


@pytest.mark.asyncio
async def test_probe_generator_128():
    prefixes = ["2001:4860:4860::8888/128\n"]
    generator = probe_generator(
        prefixes=prefixes,
        prefix_len_v6=128,
        flow_ids=[10, 11, 12],
        ttls=[41, 42],
        mapper=SequentialFlowMapper(),
    )
    probes = [x async for x in generator]
    assert len(probes) == len(set(probes)) == 6
    for addr, src_port, dst_port, ttl in probes:
        assert format_ipv6(addr) == "2001:4860:4860:0:0:0:0:8888"
        assert src_port in range(24010, 24013)
        assert dst_port == 33434
        assert ttl in range(41, 43)


@pytest.mark.asyncio
async def test_probe_generator_63():
    prefixes = ["2001:4860:4860:0000::/63\n"]
    generator = probe_generator(
        prefixes=prefixes,
        prefix_len_v6=64,
        flow_ids=[10],
        ttls=[41],
        mapper=SequentialFlowMapper(),
    )
    probes = [x async for x in generator]
    assert len(probes) == len(set(probes)) == 2
    for addr, src_port, dst_port, ttl in probes:
        assert format_ipv6(addr) in [
            "2001:4860:4860:0:0:0:0:A",
            "2001:4860:4860:1:0:0:0:A",
        ]
        assert src_port == 24000
        assert dst_port == 33434
        assert ttl == 41


@pytest.mark.asyncio
async def test_probe_generator_32():
    prefixes = ["8.8.8.8/32\n"]
    generator = probe_generator(
        prefixes=prefixes,
        prefix_len_v4=32,
        flow_ids=[10, 11, 12],
        ttls=[41, 42],
        mapper=SequentialFlowMapper(),
    )
    probes = [x async for x in generator]
    assert len(probes) == len(set(probes)) == 6
    for addr, src_port, dst_port, ttl in probes:
        assert format_ipv6(addr) == "0:0:0:0:0:FFFF:808:808"
        assert src_port in range(24010, 24013)
        assert dst_port == 33434
        assert ttl in range(41, 43)


@pytest.mark.asyncio
async def test_probe_generator_23():
    prefixes = ["0.0.0.0/23"]
    generator = probe_generator(
        prefixes=prefixes,
        prefix_len_v4=24,
        flow_ids=[10],
        ttls=[41],
        mapper=SequentialFlowMapper(),
    )
    probes = [x async for x in generator]
    assert len(probes) == len(set(probes)) == 2
    for addr, src_port, dst_port, ttl in probes:
        assert format_ipv6(addr) in [
            "0:0:0:0:0:FFFF:0:A",
            "0:0:0:0:0:FFFF:0:10A",
        ]
        assert src_port == 24000
        assert dst_port == 33434
        assert ttl == 41
