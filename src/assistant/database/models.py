"""Database metadata models."""

from typing import Optional, List, Dict, Tuple


class Column:
    """
    Represents metadata for a database column.

    This class uses `__slots__` for memory optimization, explicitly defining
    the attributes an instance can have.

    Attributes:
        table_name (str): The name of the table this column belongs to.
        name (str): The name of the column.
        data_type (Optional[str]): The SQL data type of the column (e.g., "VARCHAR", "INT").
        char_length (Optional[int]): The character length for string types.
        numeric_precision (Optional[int]): The numeric precision for numeric types.
        numeric_scale (Optional[int]): The numeric scale for numeric types.
        nullable (bool): True if the column can contain NULL values, False otherwise.
        default_value (Optional[str]): The default value for the column, if any.
        is_primary (bool): True if the column is part of the primary key, False otherwise.
        primary_key_position (Optional[int]): The 1-based position of the column in a composite primary key.
        foreign_key_ref (Optional[Tuple[str, str, str]]): A tuple (database, schema, table, column)
                                                          referencing the foreign key.
        constraints (List[Dict]): A list of dictionaries representing column-level constraints.
    """

    __slots__ = (
        "table_name",
        "name",
        "data_type",
        "char_length",
        "numeric_precision",
        "numeric_scale",
        "nullable",
        "default_value",
        "is_primary",
        "primary_key_position",
        "foreign_key_ref",
        "constraints",
    )

    def __init__(
        self,
        table_name,
        name: str,
        data_type: Optional[str] = None,
        nullable: bool = True,
        default_value: Optional[str] = None,
        is_primary: bool = False,
    ):
        """
        Initializes a new Column object.

        Args:
            table_name (str): The name of the table this column belongs to.
            name (str): The name of the column.
            data_type (Optional[str]): The SQL data type of the column. Defaults to None.
            nullable (bool): Whether the column can be null. Defaults to True.
            default_value (Optional[str]): The default value for the column. Defaults to None.
            is_primary (bool): Whether the column is part of the primary key. Defaults to False.
        """
        self.table_name = (table_name,)
        self.name = name
        self.data_type: Optional[str] = data_type
        self.nullable: bool = nullable
        self.default_value: Optional[str] = default_value
        self.is_primary: bool = is_primary
        self.char_length: Optional[int] = None
        self.numeric_precision: Optional[int] = None
        self.numeric_scale: Optional[int] = None
        self.primary_key_position: Optional[int] = None
        self.foreign_key_ref: Optional[Tuple[str, str, str]] = None
        self.constraints: List[Dict] = []  # For column-level constraints

    def __repr__(self):
        return (
            f"Column(table_name={self.table_name}, name={self.name!r}, type={self.data_type!r}, "
            f"nullable={self.nullable})"
        )


class PrimaryKey:
    """Represents Primary Key metadata."""

    __slots__ = ("name", "table_name", "columns")

    def __init__(self, name: Optional[str], table_name: str, columns: List[str]):
        self.name = name
        self.columns = columns
        self.table_name = table_name

    def __repr__(self):
        return f"PrimaryKey(name={self.name!r}, table_name={self.table_name}, columns={self.columns})"


class ForeignKey:
    """Represents foreign key metadata."""

    __slots__ = (
        "name",
        "table_name",
        "columns",
        "ref_table",
        "ref_columns",
        "ref_schema",
        "is_composite_key",
    )

    def __init__(
        self,
        name: Optional[str],
        table_name: str,
        columns: List[str],
        ref_table: str,
        ref_columns: List[str],
        ref_schema: str = None,
        is_composite_key=False,
    ):
        self.name = name
        self.table_name = table_name
        self.columns = columns
        self.ref_table = ref_table
        self.ref_columns = ref_columns
        self.is_composite_key = is_composite_key
        self.ref_schema = ref_schema

    def __repr__(self):
        return (
            f"ForeignKey(name={self.name!r}, table_name={self.table_name}, columns={self.columns}, "
            f"ref_table={self.ref_table!r}, ref_columns={self.ref_columns})"
        )


class Constraint:
    """Represents Constraint metadata."""

    __slots__ = ("name", "ctype", "expression", "columns")

    def __init__(
        self,
        name: str,
        ctype: str,
        expression: Optional[str] = None,
        columns: Optional[List[str]] = None,
    ):
        self.name = name
        self.ctype = ctype  # 'CHECK', 'UNIQUE', 'NOT NULL', etc.
        self.expression = expression
        self.columns = columns or []

    def __repr__(self):
        return f"Constraint({self.ctype}, name={self.name!r}, cols={self.columns})"


class Index:
    """Represents Index metadata."""

    __slots__ = ("name", "table", "columns", "is_unique", "method")

    def __init__(
        self,
        name: str,
        table: str,
        columns: List[str],
        is_unique: bool = False,
        method: Optional[str] = None,
    ):
        self.name = name
        self.table = table
        self.columns = columns
        self.is_unique = is_unique
        self.method = method

    def __repr__(self):
        return f"Index(name={self.name!r}, table={self.table}, columns={self.columns})"


class Table:
    """
    Represents metadata for a database table or view.

    This class uses `__slots__` for memory optimization, explicitly defining
    the attributes an instance can have.

    Attributes:
        database (Optional[str]): The name of the database where the table resides.
        schema (Optional[str]): The name of the schema where the table resides.
        name (str): The name of the table or view.
        table_type (str): The type of the table (e.g., "TABLE", "VIEW").
        columns (Dict[str, Column]): A dictionary mapping column names to Column objects.
        primary_key (Optional[PrimaryKey]): The primary key column of the table, if defined.
        foreign_keys (List[ForeignKey]): A list of ForeignKey objects.
        constraints (List[Constraint]): A list of Constraint objects (e.g., unique, check).
        is_view (bool): True if the object represents a database view, False otherwise.
        view_definition (Optional[str]): The SQL definition of the view, if `is_view` is True.
        is_materialized (bool): True if the object represents a materialized view, False otherwise.
    """

    __slots__ = (
        "database",
        "schema",
        "name",
        "table_type",
        "columns",
        "primary_key",
        "foreign_keys",
        "constraints",
        "is_view",
        "view_definition",
        "is_materialized",
    )

    def __init__(
        self,
        name: str,
        schema: Optional[str] = None,
        database: Optional[str] = None,
        table_type: str = "TABLE",
    ):
        """
        Initializes a new Table object.

        Args:
            name (str): The name of the table or view.
            schema (Optional[str]): The schema name. Defaults to None.
            database (Optional[str]): The database name. Defaults to None.
            table_type (str): The type of the table (e.g., "TABLE", "VIEW").
                              Defaults to "TABLE".
        """
        self.database = database
        self.schema = schema
        self.name = name
        self.table_type = table_type
        self.primary_key = None
        self.columns: Dict[str, Column] = {}
        self.foreign_keys: List[ForeignKey] = []
        self.constraints: List[Constraint] = []
        self.is_view = False
        self.view_definition: Optional[str] = None
        self.is_materialized = False

    def add_column(self, column: Column):
        """
        Adds a column (or primary/foreign key) to the table object.

        If the column is an instance of `ForeignKey`, it's added to `self.foreign_keys`.
        If it's an instance of `PrimaryKey`, it updates `self.primary_key`.
        Otherwise, it's added to the `self.columns` dictionary.

        Args:
            column (Column): An instance of Column, PrimaryKey, or ForeignKey.
        """
        if isinstance(column, ForeignKey):
            self.foreign_keys.append(column)
        elif isinstance(column, PrimaryKey):
            self.primary_key = column
        else:
            self.columns[column.name] = column

    def get_qualified_name(self) -> str:
        """
        Returns the fully qualified name of the table (e.g., "database.schema.table_name").

        The components (database, schema) are included only if they are not None.

        Returns:
            str: The qualified name of the table.
        """
        parts = []
        if self.database:
            parts.append(self.database)
        if self.schema:
            parts.append(self.schema)
        parts.append(self.name)
        return ".".join(parts)

    def __repr__(self):
        return (
            f"Table(name={self.get_qualified_name()}, type={self.table_type}, "
            f"columns={len(self.columns)}, pkey={self.primary_key!r})"
        )
