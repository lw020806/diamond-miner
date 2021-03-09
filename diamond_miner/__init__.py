from collections import namedtuple

from diamond_miner.mappers import (
    IntervalFlowMapper,
    RandomFlowMapper,
    ReverseByteFlowMapper,
    SequentialFlowMapper,
)
from diamond_miner.processors import next_max_ttl, next_round

MeasurementParameters = namedtuple(
    "MeasurementParameters",
    (
        "source_ip",
        "source_port",
        "destination_port",
        "min_ttl",
        "max_ttl",
        "round_number",
    ),
)


def compute_next_round(
    database_host: str,
    table_name: str,
    measurement_parameters: MeasurementParameters,
    output_file_path: str,
    mapper=IntervalFlowMapper(),
    use_max_ttl_feature=False,
    skip_unpopulated_ttl=False,
):
    with open(output_file_path, "w", newline="") as fout:
        # writer = csv.writer(fout, delimiter=",", lineterminator="\n")
        if use_max_ttl_feature:
            next_max_ttl(database_host, table_name, measurement_parameters, fout)
        next_round(
            database_host,
            table_name,
            measurement_parameters,
            mapper,
            fout,
            skip_unpopulated_ttl,
        )


__all__ = [
    "compute_next_round",
    "MeasurementParameters",
    "IntervalFlowMapper",
    "RandomFlowMapper",
    "ReverseByteFlowMapper",
    "SequentialFlowMapper",
]

__version__ = "0.1.0"