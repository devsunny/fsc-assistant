import json
import pathlib
from typing import List

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from ..config.manager import AssistantConfig

from .client import PostgreSQLClient


@click.group()
def pg_sql():
    """PostgreSQL database related commands"""
    pass


def create_pg_client(database) -> PostgreSQLClient:
    console = Console()
    config = AssistantConfig()
    dbprop = config.get_section(database)
    if not dbprop:
        console.print(
            f"[red] X {database} is not configured in .assistant.env.toml [/red] {sql_file}"
        )
        return

    if "url" in dbprop:
        database_url = dbprop["url"]
        del dbprop["url"]
        dbprop["database_url"] = database_url
    dbprop["max_conn"] = 1
    return PostgreSQLClient(**dbprop)


@click.command()
@click.option(
    "--database",
    "-d",
    type=str,
    default="database",
    help="database configuration section name in .assistant.env.toml",
)
@click.option(
    "--sql-file",
    "-s",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path
    ),
    default=None,
    help="Path to SQL script file",
)
@click.option("--sql-string", "-q", type=str, default=None, help="SQL script string")
def execute_sql(database: str, sql_file: pathlib.Path = None, sql_string: str = None):
    """simple postgresql client, execute DML and DDL statements"""
    console = Console()
    with create_pg_client(database) as dbclient:

        if sql_file is not None:
            console.print(f"[yellow]Excuting SQL File[/yellow] {sql_file}")
            dbclient.execute_sql_file(sql_file.resolve())

        if sql_string is not None:
            console.print(f"[yellow]Excuting SQL query[/yellow]")
            dbclient.execute_sql_script(sql_string)


@click.command()
@click.option(
    "--database",
    "-d",
    type=str,
    default="database",
    help="database configuration section name in .assistant.env.toml",
)
@click.option(
    "--schema-file",
    "-o",
    type=click.Path(
        exists=False, file_okay=True, dir_okay=False, path_type=pathlib.Path
    ),
    default=None,
    help="Path to schema file output",
)
@click.option(
    "--enhance",
    "-e",
    is_flag=True,
    type=bool,
    default=False,
    help="Enhance schema with column descriptions using LLM",
)
@click.option(
    "--exclude",
    "-x",
    is_flag=True,
    type=bool,
    default=False,
    help="Exclude tables when extract by schema name",
)
@click.option("--schema", "-s", type=str, help="schema name", default=None)
@click.argument("tables", type=str, nargs=-1, required=True)
def text_to_sql_schema(
    database: str,
    schema_file: pathlib.Path,
    tables: List[str],
    enhance: bool,
    exclude: bool,
    schema: str,
):
    """generate tables' schema for text to SQL"""
    console = Console()
    assert tables or schema is not None, "Either tables or schema must be specified"
    with create_pg_client(database) as dbclient:
        if not tables and schema is not None:
            tables = dbclient.get_tables(schema, exclude)
        elif tables and schema is not None and exclude is True:
            all_tables = dbclient.get_tables(schema)
            input_tables = set(
                [
                    tb.lower() if "." in tb else f"public.{tb}".lower()
                    for tb in all_tables
                ]
            )
            tables = [t for t in tables if t not in input_tables]

        if not tables:
            console.print(f"[yellow]No tables found for schema {schema}[/yellow]")
            return

        from assistant.agents.database.postgresql.metadata_builder import (
            MetadataBuilder,
        )

        metadata_builder = MetadataBuilder(dbclient)
        metadata_builder.add_all_tables(schema, *tables)

        if schema_file is not None:
            metadata_builder.build_markdown_metadata(schema_file)
            console.print(f"[green]✔ Schema is written to {schema_file}[/green]")
        else:
            console.print(Panel(Markdown(metadata_builder.build_markdown_metadata())))


@click.command()
@click.option(
    "--database",
    "-d",
    type=str,
    default="database",
    help="database configuration section name in .assistant.env.toml",
)
@click.option("--schema", "-s", type=str, help="schema name", default="public")
@click.option("--table", "-t", type=str, help="table name", required=True)
@click.argument("columns", type=str, nargs=-1, required=True)
def describe_columns(database: str, schema: str, table: str, columns: bool):
    """generate enhanced tables' column metadata for text to SQL"""
    console = Console()
    with create_pg_client(database) as dbclient:
        cols = dbclient.get_columns_data_type(schema, table, list(columns))
        descriptions = dbclient.get_column_descriptions(schema, table, cols)
        if not descriptions:
            console.print(
                f"[yellow]No descriptions found for {table}({', '.join(columns)})[/yellow]"
            )
            return

    console.print("\n\n".join(descriptions))


@click.command()
@click.option(
    "--database",
    "-d",
    type=str,
    default="database",
    help="database configuration section name in .assistant.env.toml",
)
@click.option(
    "--schema-file",
    "-s",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path
    ),
    help="Path to schema file for text to SQL",
    required=True,
)
@click.option(
    "--reload",
    "-r",
    is_flag=True,
    type=bool,
    default=False,
    help="Reload schema from file every time",
)
def text_to_sql_chat(database: str, schema_file: pathlib.Path, reload: bool):
    """PostgreSQL interactive chat with text to SQL"""
    from assistant.agents.database.postgresql.pg_agent_shell import PgAgentShell

    config = AssistantConfig()
    with create_pg_client(database) as dbclient:
        shell = PgAgentShell(schema_file, dbclient, config, reload)
        shell.run()


pg_sql.add_command(execute_sql, "execute")
pg_sql.add_command(text_to_sql_schema, "llm-schema")
pg_sql.add_command(describe_columns, "describe_columns")
pg_sql.add_command(text_to_sql_chat, "chat")
