from dataclasses import dataclass

from diamond_miner.defaults import DEFAULT_SUBSET
from diamond_miner.queries.fragments import IPNetwork
from diamond_miner.queries.query import Query


@dataclass(frozen=True)
class CreateResultsTable(Query):
    """
    Create the table used to store the measurement results from the prober.

    >>> from diamond_miner.test import execute
    >>> execute(CreateResultsTable(), "results_test")
    []
    """

    def query(self, table: str, subset: IPNetwork = DEFAULT_SUBSET) -> str:
        return f"""
        CREATE TABLE IF NOT EXISTS {table}
        (
            probe_src_addr         IPv6,
            probe_dst_addr         IPv6,
            probe_src_port         UInt16,
            probe_dst_port         UInt16,
            probe_ttl_l3           UInt8,
            probe_ttl_l4           UInt8,
            reply_src_addr         IPv6,
            reply_protocol         UInt8,
            reply_icmp_type        UInt8,
            reply_icmp_code        UInt8,
            reply_ttl              UInt8,
            reply_size             UInt16,
            rtt                    Float64,
            round                  UInt8,
            -- Materialized columns
            probe_dst_prefix       IPv6 MATERIALIZED toIPv6(cutIPv6(probe_dst_addr, 8, 1)),
            private_reply_src_addr UInt8 MATERIALIZED
                (reply_src_addr >= toIPv6('10.0.0.0')    AND reply_src_addr <= toIPv6('10.255.255.255'))  OR
                (reply_src_addr >= toIPv6('172.16.0.0')  AND reply_src_addr <= toIPv6('172.31.255.255'))  OR
                (reply_src_addr >= toIPv6('192.168.0.0') AND reply_src_addr <= toIPv6('192.168.255.255')) OR
                (reply_src_addr >= toIPv6('fd00::')      AND reply_src_addr <= toIPv6('fdff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')),
            -- ICMP: protocol 1, ICMPv6: protocol 58
            time_exceeded_reply    UInt8 MATERIALIZED (reply_protocol = 1 AND reply_icmp_type = 11) OR (reply_protocol = 58 AND reply_icmp_type = 3)
        )
            ENGINE MergeTree
                ORDER BY (probe_src_addr, probe_dst_prefix, probe_dst_addr, probe_src_port, probe_dst_port, probe_ttl_l4);
        """
