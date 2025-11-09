import json
import re
from io import StringIO

from assistant.llm.client import LLMClient
from assistant.utils.json import CustomJsonEncoder


def create_llm_client() -> LLMClient:
    return LLMClient()
