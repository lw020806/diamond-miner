from dataclasses import dataclass

from diamond_miner.queries.query import DEFAULT_SUBSET, Query  # noqa
from diamond_miner.typing import IPNetwork


@dataclass(frozen=True)
class CountNodes(Query):
    """
    Return the number of nodes discovered.
    This query does not support the ``subset`` parameter.

    >>> from diamond_miner.test import execute
    >>> execute(CountNodes(), 'test_nsdi_example')[0][0]
    7
    """

    def query(self, table: str, subset: IPNetwork = DEFAULT_SUBSET) -> str:
        assert subset == DEFAULT_SUBSET, "subset not allowed for this query"
        return f"""
        SELECT uniqExact(reply_src_addr)
        FROM {table}
        WHERE {self.common_filters(subset)}
        """
