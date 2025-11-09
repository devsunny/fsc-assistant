CUCUMBER_BBD_PROMPT = """As an expert software engineer specializing in Behavior-Driven Development (BDD), your task is to translate a given Cucumber .feature file into a complete, runnable Python module and a corresponding set of pytest unit tests.

Your response must follow these specific formatting rules:
1.  generated Python source code should be wrapped in a standard Python Markdown code block, like so:

```python
# suggestion module file name
# third party library pip install command here, e.g. "pip install psycopg2>=2.1.1"
# ... your Python code here ...
```
2. The generated pytest test code must be wrapped in a custom code block with the language name pytest, like so:

```pytest
# suggestion module file name
# ... your pytest code here ...
```
3. Do not include commentary, notes, or explanation in the output
4. for each generated class and function should also genrate python docstring
5. also generate filename suggestion as first line of code in single line comment format
6. generate third party library pip install as single line commend following file name comment

Task:

Analyze the scenarios and steps in the provided Cucumber feature file.

Create a Python module that implements the core logic described by the "Given," "When," and "Then" steps. The module should contain one or more classes and functions as necessary to fulfill the requirements.

Create a pytest test file that directly tests the implementation you've created.

Each pytest test function should correspond to a scenario from the feature file and verify the "Then" condition using assert statements.

Ensure that the tests are self-contained and do not rely on external dependencies or state.

Cucumber Feature File:

{cucumber_bdd_spec}
"""


SPEC_PROMPT = """you are a senior Python developer, you are tasked to create python software based on the user provided software Specification. Your code must strictly adhere to the following rules:
1. Filename: If the user does not specify a filename, you must generate one that is descriptive and end with .py.
2. Required Libraries: If the code uses any third-party libraries (e.g., requests, pandas, numpy), you must list them in a single-line comment immediately following the filename comment. Use a format like # Requires: library1, library2.
3. each generated class should place into their own module and each module resident in their own file according to software programming best practice
3. each module should warapped in their own code block markdown, output can have multiple python code block if necssary
4. PEP 8 Compliance: All code must follow the official PEP 8 - Style Guide for Python Code.

5. Final Format: The first line of your output must be the generated or specified filename, enclosed in a single-line Python comment (e.g., # my_script.py). The next line should list any required libraries as specified in rule #2. The code should follow, with no additional text or explanations.

software specification:
{spec}

OUTPUT RULES:
1. Do not include commentary, notes, or explanation in the output
2. file path and name should be placed before each code block like "### Filename: my/folder/my_module_name.py"
"""


ADHOC_PROMPT = """You are a Python code generation assistant. Your task is to write complete, functional, and well-structured Python code based on the user's request. Your code must strictly adhere to the following rules:

1. Filename: If the user does not specify a filename, you must generate one that is descriptive and ends with .py.
2. Required Libraries: If the code uses any third-party libraries (e.g., requests, pandas, numpy), you must list them in a single-line comment immediately following the filename comment. Use a format like # Requires: library1, library2.
3. PEP 8 Compliance: All code must follow the official PEP 8 - Style Guide for Python Code. This includes proper indentation, spacing, variable naming conventions (e.g., snake_case), and line length limits.
4. Docstrings: All functions, methods, classes, and modules must include a comprehensive docstring. The docstring should explain the purpose of the code block, list all parameters with their types and a brief description, and describe the return value. Use a standard docstring format like Google Style Guide or Numpy Style.
5. Final Format: The first line of your output must be the generated or specified filename, enclosed in a single-line Python comment (e.g., # my_script.py). The next line should list any required libraries as specified in rule #2. The code should follow, with no additional text or explanations.

User Request:
{prompt}
        
OUTPUT RULES:
1. Do not include commentary, notes, or explanation in the output
2. for each generated class and function should also genrate python docstring
3. also generate filename suggestion as first line of code in single line comment format

output example
```python
# cpu_calculator.copy
class CpuCalculator:
    def __init__(self, *args):
        self.args =args
    
    def do_something(self):
        '''doing some funny thing here'''
    
    def do_more_things(self):
        '''doing more funny thing here'''
```    
"""


ADF_TO_PYTHON_PROMPT = """you are a senior data engineer and experts in python, Azure Data Factory (ADF), you are tasked to convert ADF script to python with:

1. use utility functions from bg_utils , these functions should be used instead of functions in pandas module
2. include the following import statements
```python
import bg_api as etl
from bg_utility import *
from schemas.schema import *
```
3. transfommer claass should extends etl.ETLTransformBase, see example below
```python
DEFAULT_META = bg.ETLMETADATA("2024-08-24", "MAKO_SS_AUG_2024_001_V1", "MAKO_SS_AUG_2024_003", "2024-08-24")
@etl.BridgeETLTransform("_020_GenT2JointChar")
class Transform_020_GenT2JointChar(etl.ETLTransformBase):
    def __init__(self, project_name):
        super().__init__(project_name)

```

```python
DEFAULT_META = bg.ETLMETADATA("2024-08-24", "MAKO_SS_AUG_2024_001_V1", "MAKO_SS_AUG_2024_003", "2024-08-24")
@etl.BridgeETLTransform("_020_GenT2JointChar")
class Transform_020_GenT2JointChar(etl.ETLTransformBase):
    def __init__(self, project_name):
        super().__init__(project_name)

```
4. transform function should be decorated with "@etl.BridgeETLFunc()"
```python
@etl.BridgeETLFunc()
    def run_Main(self, inLDTIPolicyExtractGDS, HoldFunds02, FAS133PremIF02DirAltSelect, InLDITTransactionsGDSselect1, METADATA):
    ...
```

--------
{bg_utility}
--------

## Source Code
{source_code}




## Sample input file
{input}

--------

## Sample output file
{output}


# OUTPUT FORMAT:
1. use the pandas library
2. output all python classes and functions in one file
3. generate python requirements.txt file
4. output file should have main function and executable
5. place file path and name before code block, such as "### Filename: my/folder/module_name.py\n```python\n...\n```\n"
"""

BG_UTILITY = '''## Filename: bg_utility.py
```python
load_data(transform, table_schema, str_file_data, config_string = "", desc=""):
    """
    Load Data and Schema into a Table.

    This function will load data and schema information into a Table that can be transformed usint the ETL API functions.

    Args:
        table (Table): A table with a schema and data.
        str_file_data (string): Name of file to load.
        ext (string): Extension of file to load.
        delimiter (string): The character the separates one data value from another in the file.  

    Returns:
        table (Table): The resulting table after the transformation.
    """    
	
	
output_table(cfg, transform, table, str_out_filename, desc=""):
    """
    Output table into a file.

    This function will Output the table headers and data into a .csv file.

    Args:
        table (Table): A table with a schema and data.
        str_out_filename (string): Name of file to write.
        b_include_headers (bool): Include headers in output.

    Returns:
        Does not return a value
    """


duplicate_col(table, copy_col_vector, desc=""):
    """
    Adds new col(s) with a copy of an existing col(s)
    
    Args:
        table (Table): A table with a schema and data.
        copy_col_vector (Nx2): Old / New

    Returns:
        table (Table): The resulting table after the transformation.
    """
	
	
add_or_update_col_multi(table, function_dict, desc=""):
    """
    Add or Update a column in the table.

    This function will Add a column to the table if the column name does not already exist in the table. If the column name exists, it will Update that column's data with the values evaluated from the 'function'.

    Args:
        table (Table): A table with a schema and data.
        column_info (list (2 strings)): The column info consisting of ["<Column Name>", "<Data Type>"]
        function (callable): A function or lambda to run for each row to determine the data value for that row

    Returns:
        table (Table): The resulting table after the transformation.
    """
	
drop_cols(table, cols_to_drop, desc=""):
    """
    Drop(s) Column(s) in the table    

    This function will drop column(s) in the table if they exist. Bad column names will have no affect.

    Args:
        table (Table): A table with a schema and data.
        cols_to_drop (string or array[N]): The column(s) to drop        

    Returns:
        table (Table): The resulting table after the transformation.
    """
	
	
rename(table, column_to_rename, new_column_name, desc=""):
    """
    Rename a column in the table.

    This function will Rename a column in the table if the column name exist in the table. If the column name does not exist, it will do nothing.

    Args:
        table (Table): A table with a schema and data.
        column_to_rename (string): The current name of the column to be renamed
        new_column_name (string): The new name for the column

    Returns:
        table (Table): The resulting table after the transformation.
    """
	


select(table, column_names_to_select, desc=""):
    """
    Select columns to keep from a table - remove the rest.

    This function will preserve columns specified in 'column_names_to_select'. The rest will be removed from the table.

    Args:
        table (Table): A table with a schema and data.
        column_names_to_select (list (n strings)): The column names of the columns to keep.

    Returns:
        table (Table): The resulting table after the transformation.
    """


filter(table, condition_function, desc=""):
    """
    Filter rows to keep from a table - remove the rest.

    This function will preserve rows where the 'condition_function' for the row evaluates to 'True'. The rest will be removed from the table.

    Args:
        table (Table): A table with a schema and data.
        condition_function (callable): Function to evaluate for each row. Must result in 'True' or 'False'.

    Returns:
        table (Table): The resulting table after the transformation.
    """
	
split(table, condition_functions, matching_condition:MatchingCondition=MatchingCondition.First, desc=""):
    """
    Split table into multple tables depending on conditions.

    This function will Split tables into multiple tables depending on the conditions passed in and the 'matching_condition' configuration. Number of resulting tables is (len(condition_functions) + 1)

    Args:
        table (Table): A table with a schema and data.
        condition_functions (list(n callables)): Function to evaluate for each row. Must result in 'True' or 'False'.
        matching_condition (MatchingCondition): The rule in which to divide rows. 'First' will only put a row into the new table with the first matching condition. 'All' will put the row in all tables that match the condition. 

    Returns:
        table (Table): The resulting table after the transformation.
    """


union(table1, table2, union_by:UnionBy=UnionBy.Name, desc=""):
    """
    Union table into multple tables depending on conditions.

    This function will Union 2 tables together into a single table.

    Args:
        table1 (Table): A table with a schema and data.
        table2 (Table): A table with a schema and data.
        union_by (UnionBy): How to Union the tables. UnionBy.Name will merge by column name. UnionBy.Position will merge on column position.

    Returns:
        table (Table): The resulting table after the transformation.
    """
	
aggregate(table, groupby_column_names, aggregate_expressions, desc=""):
    """
    Aggregate values of a column based on GroupBy column combination and aggregate function.

    This function will Aggregate data in a table. EvalScalars are aggregated on a column combination basis specified in 'groupby_column_names'.

    Args:
        table (Table): A table with a schema and data.
        groupby_column_names (list(n strings)): Columns to serve as key combination to aggregate values on.
        aggregate_expressions (list(n expressions)): New Columns to create with aggregated results based on expression.

    Returns:
        table (Table): The resulting table after the transformation.
    """

unpivot(
        table,
        ungroupby_column_names,
        key_column_info,
        unpivot_columns_info,
        unpivot_type =ColumnArrangement.Lateral,
        desc=""
):
    """
    Unpivot column names into data values of a specified new column.

    This function will Unpivot data in a table.

    Args:
        table (Table): A table with a schema and data.
        ungroupby_column_names (list(n strings)): Columns to keep.
        key_column_info (list(2 strings)): New Columns to hold unpivoted column names.
        unpivot_columns_info (list(list (2 strings))): Columns to unpivot.
        unpivot_type (ColumnArrangement): Type of Unpivot. Must be ColumnArrangement.Lateral or ColumnArrangement.Normal.

    Returns:
        table (Table): The resulting table after the transformation.
    """
	
join(left_table, right_table, join_conditions, join_type:JoinType=JoinType.LeftOuter, suffix_info=("_RIGHT", SuffixOnMatch.ERROR), desc=""):
    """
    Join 2 columsn into a single column.

    This function will Join 2 columns.

    Args:
        left_table (Table): A table with a schema and data.
        right_table (Table): A table with a schema and data.
        join_conditions (list(n conditions)): Conditions to determine which rows from left_table are joined with their respective rows in right_table.
        jointype (JoinType): The type of Join.

    Returns:
        table (Table): The resulting table after the transformation.
    """


cross_join(left_table, right_table, conditions=None, desc=""):
    """
    Cross Join 2 tables together. (Cartesian Product)

    This function will Cross Join 2 tables where each row from the left_table is paired with every row from the right_table.

    Args:
        left_table (Table): A table with a schema and data.
        right_table (Table): A table with a schema and data.
        conditions (list(n conditions)): Condition to determine which resulting rows to keep from the cross join. (Optional - keeps all rows if not defined)

    Returns:
        table (Table): The resulting table after the transformation.
    """
	
update_matching_cols(
        table,
        evalulation_col,
        evalulation_value,
        desc=""
):
    """
    Update Columns by condition.

    This function will evaluate a 'evalulation_col' function and will update columns that return 'True' for the condition with the value resulting from the 'evalulation_value' function.

    Args:
        table (Table): A table with a schema and data.
        evalulation_col (callable): Condition to find columns.
        evalulation_value (callable): Expression to determine new value for row in updating column.

    Returns:
        table (Table): The resulting table after the transformation.
    """


pivot(table, 
        groupby_column_names,
        pivot_key,
        pivot_expressions,
        pivot_type = ColumnArrangement.Lateral,
        desc = ""
        ):
    """
    Pivot column names into data values of a specified new column.

    This function will Pivot data in a table.

    Args:
        table (Table): A table with a schema and data.
        groupby_column_names (list(n str)): Columns to keep.
        pivot_key (tuple): A tuple of (column_name, values_list) where column_name is the column to pivot on and values_list is a list of values to create columns for.
        pivot_expressions (list(list (str, callable))): Column Prefix and pivot expression.
        pivot_type (ColumnArrangement): Must be ColumnArrangement.Lateral or ColumnArrangement.Normal.

    Returns:
        table 

lookup(primary_table, lookup_table, lookup_conditions, match_on : MatchOn = MatchOn.Any, suffix_info=("_RIGHT", SuffixOnMatch.Right), desc=""):
    """
    Lookup 

    This function will Lookup data to add to the Primary table based on lookup conditions.

    Args:
        primary_table (Table): A table with a schema and data.
        lookup_table (Table): A table with a schema and data.
        conditions (list(n conditions)): Conditions to determine which rows in the lookup_table map to rows in the primary primary_table.

    Returns:
        table (Table): The resulting table after the transformation.
    """

window(table, over, sort, window_columns, desc=""):
    """
    Window 

    This function will perform window operations on a table, allowing aggregations over partitioned data.

    Args:
        table (Table): A table with a schema and data.
        over (list): List of column names to partition by.
        sort (list): List of column names to sort within each partition.
        window_columns (list): List of window column definitions, each containing:
            - name: Name for the new column
            - function: Aggregation function to apply (sum, avg, count, etc)
            - source_column: Column to aggregate

    Returns:
        table (Table): The resulting table after the window operations.
    """


surrogate_key(table, column_name, start_value, step_value, desc=""):
    """
    Surrogate Key 

    This function will add an incrementing integer value to each row.

    Args:
        table (Table): A table with a schema and data.
        column_name (str): The name of the new column.
        start_value (int): The number to start. The number for the first row.
        step_value (int): The number to increment.

    Returns:
        table (Table): The resulting table after the transformation.
    """


sort(table, cols_list, case_sensitive=False, desc=""):
    """
    Sort 

    This function will sort specified rows in the table.

    Args:
        table (Table): A table with a schema and data.
        cols_list (tuple): Tuple of (ColName, Ascending, NullsFirst)
        case_sensitive (bool): Sort case sensitive

    Returns:
        table (Table): The resulting table after the transformation.
    """

```
'''
