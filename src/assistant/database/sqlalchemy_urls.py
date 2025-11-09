"""Utility functions for SQLAlchemy URL construction."""


def get_sqlalchemy_url(db_name: str, **kwargs) -> str:
    """
    Returns a formatted SQLAlchemy database URL based on a template and provided keyword arguments,
    using f-strings for construction.

    Args:
        db_name (str): The name of the database (e.g., "mysql", "snowflake").
        **kwargs: Keyword arguments containing the values to substitute into the URL.

    Returns:
        str: The formatted database URL.

    Raises:
        ValueError: If the db_name is not supported or if a required variable for the
                    template is missing from kwargs.
    """

    if db_name == "sqlite":
        return "sqlite:///:memory:"

    # Dictionary to store parameter requirements for each database type
    # Note: 'databricks' has no specific URL parameters in this context.
    required_params = {
        "mysql": ["user", "password", "host", "port", "database"],
        "oracle": ["user", "password", "host", "port", "database"],
        "postgresql": ["user", "password", "host", "port", "database"],
        "mssql": ["user", "password", "host", "port", "database"],
        "redshift": ["user", "password", "host", "port", "database"],
        "snowflake": ["user", "password", "account", "database", "schema"],
        "databricks": ["access_token", "host", "http_path", "catalog", "schema"],
    }

    # Create a mutable copy of kwargs and set default values for optional parameters
    params = {**kwargs}
    params.setdefault("warehouse", "")  # Default for Snowflake
    params.setdefault("role", "")  # Default for Snowflake

    # Check if the database name is supported
    if db_name not in required_params:
        raise ValueError(
            f"Database name '{db_name}' not supported or found in URL templates."
            f"Supported database are {required_params.keys()}"
        )

    # Helper function to check for missing required parameters
    def _check_missing_params(db: str, current_params: dict, req_keys: list):
        for key in req_keys:
            if key not in current_params:
                raise ValueError(
                    f"Missing required variable for {db} URL: '{key}'. "
                    "Please provide it in the keyword arguments."
                )

    # Construct the URL using f-strings based on the database name
    if db_name == "databricks":
        _check_missing_params(db_name, params, required_params["databricks"])
        return (
            f"databricks://token:{params['access_token']}"
            f"@{params['host']}?http_path={params['http_path']}&"
            f"catalog={params['catalog']}&schema={params['schema']}"
        )
    elif db_name == "mysql":
        _check_missing_params(db_name, params, required_params["mysql"])
        return (
            f"mysql+mysqlconnector://"
            f"{params['user']}:{params['password']}@{params['host']}:"
            f"{params['port']}/{params['database']}"
        )
    elif db_name == "oracle":
        _check_missing_params(db_name, params, required_params["oracle"])
        return (
            f"oracle+oracledb://"
            f"{params['user']}:{params['password']}@{params['host']}:"
            f"{params['port']}/{params['database']}"
        )
    elif db_name == "postgresql":
        _check_missing_params(db_name, params, required_params["postgresql"])
        return (
            f"postgresql+psycopg2://"
            f"{params['user']}:{params['password']}@{params['host']}:"
            f"{params['port']}/{params['database']}"
        )
    elif db_name == "mssql":
        _check_missing_params(db_name, params, required_params["mssql"])
        return (
            f"mssql+pyodbc://"
            f"{params['user']}:{params['password']}@{params['host']}:"
            f"{params['port']}/{params['database']}?driver=ODBC+Driver+18+for+SQL+Server"
        )
    elif db_name == "redshift":
        _check_missing_params(db_name, params, required_params["redshift"])
        return (
            f"redshift+redshift_connector://"
            f"{params['user']}:{params['password']}@{params['host']}:"
            f"{params['port']}/{params['database']}"
        )
    elif db_name == "snowflake":
        _check_missing_params(db_name, params, required_params["snowflake"])
        return (
            f"snowflake://"
            f"{params['user']}:{params['password']}@{params['account']}/"
            f"{params['database']}/{params['schema']}?"
            f"warehouse={params['warehouse']}&role={params['role']}"
        )
    # This else block should ideally not be reached due to the initial check
    else:
        raise ValueError(f"Internal error: Unhandled database name '{db_name}'.")
