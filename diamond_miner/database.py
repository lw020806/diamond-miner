from aioch import Client

from diamond_miner.queries import CreateFlowsView, CreateLinksTable, CreateResultsTable


def table_name(table: str, suffix: str) -> str:
    return table + suffix.replace("-", "_")


async def create_tables(client: Client, suffix: str):
    await CreateResultsTable().execute_async(client, table_name("results", suffix))
    await CreateFlowsView(parent=table_name("results", suffix)).execute_async(
        client, table_name("flows", suffix)
    )
    await CreateLinksTable().execute_async(client, table_name("links", suffix))


async def drop_tables(client: Client, suffix: str):
    for table in ["results", "flows", "links"]:
        await client.execute(f"DROP TABLE IF EXISTS {table_name(table, suffix)}")
