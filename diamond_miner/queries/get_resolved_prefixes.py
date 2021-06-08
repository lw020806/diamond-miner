from dataclasses import dataclass

from diamond_miner.queries.query import UNIVERSE_SUBSET, ResultsQuery, results_table
from diamond_miner.typing import IPNetwork


@dataclass(frozen=True)
class GetResolvedPrefixes(ResultsQuery):
    """
    Return the prefixes for which no replies have been received at the previous round
    (i.e. no probes have been sent, most likely).

    >>> from diamond_miner.test import addr_to_string, client
    >>> GetResolvedPrefixes(round_leq=1).execute(client, 'test_nsdi_example')
    []
    >>> prefixes = GetResolvedPrefixes(round_leq=5).execute(client, 'test_nsdi_example')
    >>> [(x[0], addr_to_string(x[1])) for x in prefixes]
    [(1, '200.0.0.0')]
    """

    def query(self, measurement_id: str, subset: IPNetwork = UNIVERSE_SUBSET) -> str:
        assert self.round_leq is not None
        return f"""
        SELECT DISTINCT probe_protocol, probe_dst_prefix
        FROM {results_table(measurement_id)}
        WHERE {self.filters(subset)}
        GROUP BY (probe_protocol, probe_src_addr, probe_dst_prefix)
        HAVING max(round) < {self.round_leq - 1}
        """
