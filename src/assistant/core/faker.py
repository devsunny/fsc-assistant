import json
from typing import Dict, List

from pgsql_parser import Column, Table

from ..llm.client import llmclient
from ..utils.cli.utils import get_config, load_atlas_env


class DataGenerator:
    def __init__(self, table: Table):
        self.llm_model_id = get_config("model_id", "llm")
        self.table = table

    def _get_column_defintion(self) -> List[Dict]:

        def to_dict(col: Column):
            return {
                "column_name": col.name,
                "data_type": col.data_type,
                "char_length": col.char_length,
                "numeric_precision": col.numeric_precision,
                "numeric_scale": col.numeric_scale,
                "nullable": col.nullable,
            }

        return [to_dict(col) for col in self.table.columns.values()]

    def generate_fake_data(self, num: int = 1):
        howmany = "one record" if num <= 1 else f"{num} records"
        column_defs = json.dumps(self._get_column_defintion(), indent=2)

        sample_prompt = f"""
you are tasked to generate fake testing data based table column defintion with:

1. output data in json format
2. no explanation, notes and comments in output
3. for datetime and timestamp data, use ISO 8601 format
4. generate {howmany}

```json
{column_defs}
```
        """
        result = llmclient.invoke_model(
            prompt=sample_prompt, max_completion_tokens=4096
        )
        return result
