"""Database metadata extractor using SQLAlchemy."""

import re
import logging
from typing import Optional, List

import boto3
import botocore.client
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

from .models import Table, Column, PrimaryKey, ForeignKey, Constraint, Index
from .sqlalchemy_urls import get_sqlalchemy_url


logger = logging.getLogger(__name__)


def get_aws_secret(
    secret_name,
    region_name="us-east-1",
    aws_access_key_id=None,
    aws_secret_access_key=None,
    aws_session_token=None,
    **kwargs,
):
    """
    Retrieve AWS secret from AWS Secrets Manager.

    Args:
        secret_name: Secret name or ARN. If prefixed with "AWS://", will lookup in Secrets Manager.
        region_name: AWS region name. Defaults to "us-east-1".
        aws_access_key_id: AWS access key ID (optional).
        aws_secret_access_key: AWS secret access key (optional).
        aws_session_token: AWS session token (optional).
        **kwargs: Additional keyword arguments (e.g., logger).

    Returns:
        str: The secret value or the original secret_name if not found in AWS.
    """
    local_logger = kwargs.get("logger") or logger
    if secret_name is None:
        return None
    name = secret_name
    if secret_name.startswith("AWS://") and len(secret_name) > 6:
        name = secret_name[6:]
    else:
        return name
    try:
        client = boto3.client(
            "secretsmanager",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )
        local_logger.info("secretsmanager lookup:%s", name)
        response = client.get_secret_value(SecretId=name)
        if response:
            return response["SecretString"]
        return name
    except botocore.exceptions.ClientError as err:
        local_logger.exception(err)
        return secret_name


class SQLAlchemyMetadataExtractor:
    """
    A class to extract database table metadata using SQLAlchemy's reflection capabilities.

    It connects to a database via a SQLAlchemy URL and provides methods to retrieve
    detailed information about tables, columns, primary keys, foreign keys,
    constraints, and indexes, populating custom metadata objects.

    Attributes:
        engine (Engine): The SQLAlchemy engine connected to the database.
        inspector (Inspector): The SQLAlchemy inspector object for database introspection.
    """

    def __init__(self, **kwargs):
        """
        Initializes the MetadataExtractor with a database connection URL.

        Args:
            **kwargs: Database connection parameters including:
                - type/dbtype/db_type/database_basename: Database type (e.g., "postgresql")
                - user: Database username
                - password: Database password (can be AWS secret with "AWS://" prefix)
                - host: Database host
                - port: Database port
                - database: Database name
                - schema: Database schema (optional)

        Raises:
            SQLAlchemyError: If there's an issue connecting to the database.
        """
        try:
            database_basename = (
                kwargs.get("type")
                or kwargs.get("dbtype")
                or kwargs.get("db_type")
                or kwargs.get("database_basename")
            )
            conn_info = {**kwargs}
            password = conn_info.get("password", None)
            if password:
                conn_info["password"] = get_aws_secret(password)

            db_url = get_sqlalchemy_url(database_basename, **conn_info)
            self.engine = create_engine(db_url)
            self.inspector = inspect(self.engine)
            # Test connection
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info(
                "Successfully connected to the [%s] database.", database_basename
            )
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to connect to the database: {e}") from e

    def get_all_schemas(self) -> List[str]:
        """
        Retrieves a list of all schema names available in the connected database.

        Returns:
            List[str]: A list of schema names.

        Raises:
            SQLAlchemyError: If there's an issue retrieving schema names.
        """
        try:
            return self.inspector.get_schema_names()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error retrieving schema names: {e}") from e

    def get_tables_in_schema(self, schema: Optional[str] = None) -> List[str]:
        """
        Retrieves a list of all table names within a specified schema.

        Args:
            schema (Optional[str]): The schema name to retrieve tables from.
                                    If None, retrieves from the default schema.

        Returns:
            List[str]: A list of table names within the specified schema.

        Raises:
            SQLAlchemyError: If there's an issue retrieving table names.
        """
        try:
            return self.inspector.get_table_names(schema=schema)
        except SQLAlchemyError as e:
            raise SQLAlchemyError(
                f"Error retrieving table names for schema '{schema}': {e}"
            ) from e

    def get_views_in_schema(self, schema: Optional[str] = None) -> List[str]:
        """
        Retrieves a list of all view names within a specified schema.

        Args:
            schema (Optional[str]): The schema name to retrieve views from.
                                    If None, retrieves from the default schema.

        Returns:
            List[str]: A list of view names within the specified schema.

        Raises:
            SQLAlchemyError: If there's an issue retrieving view names.
        """
        try:
            return self.inspector.get_view_names(schema=schema)
        except SQLAlchemyError as e:
            raise SQLAlchemyError(
                f"Error retrieving view names for schema '{schema}': {e}"
            ) from e

    def get_table_metadata(
        self,
        table_name: str,
        schema: Optional[str] = None,
    ) -> Table:
        """
        Retrieves metadata for a single table.

        Args:
            table_name: Name of the table (can include schema as "schema.table").
            schema: Schema name (optional, overridden if table_name includes schema).

        Returns:
            Table: Table metadata object.

        Raises:
            ValueError: If the table is not found.
        """
        if "." in table_name:
            parts = table_name.split(".")
            schema = parts[0].strip()
            table_name = parts[1].strip()

        table_metadatas = self.get_all_table_metadata(
            schema=schema, target_tables=[table_name]
        )
        if table_metadatas:
            return table_metadatas[0]
        raise ValueError(f"table [{table_name}] not found")

    def get_all_table_metadata(
        self,
        schema: Optional[str] = None,
        include_views: bool = True,
        target_tables: Optional[List[str]] = None,
    ) -> List[Table]:
        """
        Extracts metadata for all tables (and optionally views) in the specified schema.

        Args:
            schema (Optional[str]): The schema name to extract tables from.
                                    If None, extracts from the default schema.
            include_views (bool): If True, also includes views in the metadata extraction.
                                  Defaults to True.
            target_tables (Optional[List[str]]): List of specific table names to extract.
                                                 If None or empty, extracts all tables.

        Returns:
            List[Table]: A list of Table objects, each containing comprehensive metadata.

        Raises:
            SQLAlchemyError: If there's an issue during metadata extraction.
        """
        if target_tables is None:
            target_tables = []

        tables_metadata: List[Table] = []
        try:
            table_names = self.inspector.get_table_names(schema=schema)
            if include_views:
                view_names = self.inspector.get_view_names(schema=schema)
                # Combine and remove duplicates if any (though unlikely for table/view names)
                all_names = list(set(table_names + view_names))
            else:
                all_names = table_names

            if target_tables:
                target_tables = [tbname.strip().upper() for tbname in target_tables]
                all_names = [
                    tbname for tbname in all_names if tbname.upper() in target_tables
                ]

            for table_name in all_names:
                table_type = "TABLE"
                is_view = False
                view_definition = None

                if include_views and table_name in self.inspector.get_view_names(
                    schema=schema
                ):
                    table_type = "VIEW"
                    is_view = True
                    # Attempt to get view definition if supported by dialect
                    try:
                        view_definition = self.inspector.get_view_definition(
                            table_name, schema=schema
                        )
                        if view_definition:
                            view_definition = str(view_definition).strip()
                    except NotImplementedError:
                        view_definition = None  # Not all dialects support this

                table_obj = Table(name=table_name, schema=schema, table_type=table_type)
                table_obj.is_view = is_view
                table_obj.view_definition = view_definition

                # Get Columns
                self._populate_columns(table_obj, schema)

                # Get Primary Key
                self._populate_primary_key(table_obj, schema)

                # Get Foreign Keys
                self._populate_foreign_keys(table_obj, schema)

                # Get Constraints (Unique, Check)
                self._populate_constraints(table_obj, schema)

                # Get Indexes
                self._populate_indexes(table_obj, schema)

                tables_metadata.append(table_obj)

        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error during metadata extraction: {e}") from e
        return tables_metadata

    def _populate_columns(self, table_obj: Table, schema: Optional[str]):
        """Helper to populate Column objects for a given Table."""
        columns_info = self.inspector.get_columns(table_obj.name, schema=schema)
        for col_info in columns_info:
            data_type = str(col_info["type"])
            rematch = re.search(r"^([A-Za-z0-9]+)[(].+$", data_type, re.IGNORECASE)
            if rematch:
                data_type = rematch.group(1)
            column = Column(
                table_name=table_obj.name,
                name=col_info["name"],
                data_type=data_type,
                nullable=col_info.get("nullable", True),
                default_value=col_info.get("default"),
                # is_primary and primary_key_position will be set by _populate_primary_key
                # foreign_key_ref will be set by _populate_foreign_keys
            )
            # Populate additional type-specific attributes
            if hasattr(col_info["type"], "length"):
                column.char_length = col_info["type"].length
            if hasattr(col_info["type"], "precision"):
                column.numeric_precision = col_info["type"].precision
            if hasattr(col_info["type"], "scale"):
                column.numeric_scale = col_info["type"].scale

            table_obj.add_column(column)  # Add to the table_obj.columns dictionary

    def _populate_primary_key(self, table_obj: Table, schema: Optional[str]):
        """Helper to populate PrimaryKey object and update Column objects."""
        pk_constraint = self.inspector.get_pk_constraint(table_obj.name, schema=schema)
        if pk_constraint and pk_constraint.get("constrained_columns"):
            pk_name = pk_constraint.get("name")
            pk_columns = pk_constraint["constrained_columns"]
            table_obj.primary_key = PrimaryKey(
                name=pk_name, table_name=table_obj.name, columns=pk_columns
            )
            for i, col_name in enumerate(pk_columns):
                if col_name in table_obj.columns:
                    table_obj.columns[col_name].is_primary = True
                    table_obj.columns[col_name].nullable = False
                    table_obj.columns[col_name].primary_key_position = i + 1

    def _populate_foreign_keys(self, table_obj: Table, schema: Optional[str]):
        """Helper to populate ForeignKey objects and update Column objects."""
        fks_info = self.inspector.get_foreign_keys(table_obj.name, schema=schema)
        for fk_info in fks_info:
            fk_name = fk_info.get("name")
            constrained_columns = fk_info["constrained_columns"]
            referred_table = fk_info["referred_table"]
            referred_columns = fk_info["referred_columns"]
            referred_schema = fk_info.get("referred_schema")

            foreign_key = ForeignKey(
                name=fk_name,
                table_name=table_obj.name,
                columns=constrained_columns,
                ref_table=referred_table,
                ref_columns=referred_columns,
                ref_schema=referred_schema,
                is_composite_key=len(constrained_columns) > 1,
            )
            table_obj.foreign_keys.append(foreign_key)

            # Update individual Column objects with foreign_key_ref
            for i, col_name in enumerate(constrained_columns):
                if col_name in table_obj.columns:
                    # Note: foreign_key_ref stores (ref_schema, ref_table, ref_column)
                    table_obj.columns[col_name].foreign_key_ref = (
                        referred_schema,
                        referred_table,
                        referred_columns[i] if i < len(referred_columns) else None,
                    )

    def _populate_constraints(self, table_obj: Table, schema: Optional[str]):
        """Helper to populate Constraint objects (Unique, Check)."""
        unique_constraints = self.inspector.get_unique_constraints(
            table_obj.name, schema=schema
        )

        for uc_info in unique_constraints:
            table_obj.constraints.append(
                Constraint(
                    name=uc_info.get("name", "anon_unique"),
                    ctype="UNIQUE",
                    columns=uc_info.get("column_names"),
                )
            )

        check_constraints = self.inspector.get_check_constraints(
            table_obj.name, schema=schema
        )
        for cc_info in check_constraints:
            table_obj.constraints.append(
                Constraint(
                    name=cc_info.get("name", "anon_check"),
                    ctype="CHECK",
                    expression=str(cc_info.get("sqltext")),
                )
            )

    def _populate_indexes(self, table_obj: Table, schema: Optional[str]):
        """Helper to populate Index objects."""
        indexes_info = self.inspector.get_indexes(table_obj.name, schema=schema)
        for idx_info in indexes_info:
            table_obj.constraints.append(  # Indexes are often treated as constraints in metadata
                Index(
                    name=idx_info.get("name"),
                    table=table_obj.name,
                    columns=idx_info.get("column_names"),
                    is_unique=idx_info.get("unique", False),
                    method=idx_info.get("dialect_options", {}).get(
                        "postgresql_using"
                    ),  # Example for PostgreSQL
                )
            )
