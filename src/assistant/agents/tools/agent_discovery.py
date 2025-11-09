import enum
import inspect
import re
import textwrap
import typing
from typing import (
    Annotated,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    get_args,
    get_origin,
)

_JSON_PRIMITIVES = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
}


def _first_line(s: str) -> str:
    if not s:
        return ""
    s = textwrap.dedent(s).strip()
    return s.splitlines()[0].strip() if s else ""


def _parse_doc_params(doc: str) -> dict:
    """
    Return {param_name: description} parsed from common docstring styles:
      - Sphinx:   :param name: desc
      - Google:   Args:\n  name (type): desc
      - NumPy:    Parameters\n----------\nname : type\n    desc
    """
    if not doc:
        return {}

    doc = textwrap.dedent(doc)

    results = {}

    # --- Sphinx-style ":param name: desc"
    for name, desc in re.findall(r":param\s+([*\w]+)\s*:\s*(.+)", doc):
        results[name] = desc.strip()

    # --- Google-style "Args:" blocks
    google_args_block = re.search(r"(?ms)^Args:\s*(.+?)(?:^\S|\Z)", doc)
    if google_args_block:
        block = google_args_block.group(1)
        # Lines like: "name (type): description" OR "name: description"
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"^([*\w]+)\s*(?:\([^)]+\))?\s*:\s*(.+)$", line)
            if m:
                results[m.group(1)] = m.group(2).strip()

    # --- NumPy-style "Parameters" section
    numpy_block = re.search(r"(?ms)^Parameters\s*-+\s*(.+?)(?:^\S|\Z)", doc)
    if numpy_block:
        block = numpy_block.group(1)
        # Pattern: "name : type" on one line; following indented lines are description
        # Split on blank lines between entries
        chunks = re.split(r"\n\s*\n", block.strip())
        for ch in chunks:
            first, *rest = ch.splitlines()
            m = re.match(r"^\s*([*\w]+)\s*:\s*.+$", first.strip())
            if m:
                name = m.group(1)
                desc = " ".join(rest).strip()
                if desc:
                    results[name] = desc

    return results


def _unwrap_optional(ann):
    """Return (base_type, is_optional) for Optional/Union[..., None]."""
    origin = get_origin(ann)
    if origin is typing.Union:
        args = [a for a in get_args(ann) if a is not type(None)]
        if len(args) == 1:
            return args[0], True
    return ann, False


def _annotation_to_schema(ann):
    """
    Convert a Python annotation into a JSON Schema snippet (no 'description', no 'required').
    Handles: primitives, Optional/Union, Literal, Enum, List[T], Dict[K,V], tuple, Annotated.
    Falls back to 'string' for unknowns.
    """
    if ann is inspect._empty or ann is None:
        return {"type": "string"}

    # Handle typing.Annotated[T, ...]
    origin = get_origin(ann)
    if origin is Annotated:
        ann = get_args(ann)[0]  # Get the first argument (the actual type)
        origin = get_origin(ann)

    # Optional / Union[..., None]
    base, is_optional = _unwrap_optional(ann)
    ann = base
    origin = get_origin(ann)

    # Enum subclass
    if inspect.isclass(ann) and issubclass(ann, enum.Enum):
        values = [e.value for e in ann]  # best effort
        # Map enum values to a consistent JSON type
        if all(isinstance(v, str) for v in values):
            return {"type": "string", "enum": values}
        elif all(isinstance(v, int) for v in values):
            return {"type": "integer", "enum": values}
        else:
            # mixed types - use string representation as fallback
            return {"type": "string", "enum": [str(v) for v in values]}

    # Literal
    if origin is typing.Literal:
        vals = get_args(ann)
        # Infer type from first literal value
        if vals:
            val_type = type(vals[0])
            if val_type == str:
                return {"type": "string", "enum": list(vals)}
            elif val_type == int:
                return {"type": "integer", "enum": list(vals)}
            elif val_type == bool:
                return {"type": "boolean", "enum": list(vals)}
        return {"type": "string", "enum": [str(v) for v in vals]}

    # Builtin primitives
    if ann in _JSON_PRIMITIVES:
        return {"type": _JSON_PRIMITIVES[ann]}

    # List / Sequence
    if origin in (list, typing.List, typing.Sequence, typing.MutableSequence):
        item_ann = get_args(ann)[0] if get_args(ann) else Any
        item_schema = _annotation_to_schema(item_ann)
        return {"type": "array", "items": item_schema}

    # Dict / Mapping
    if origin in (dict, typing.Dict, typing.Mapping, typing.MutableMapping):
        args = get_args(ann)
        if len(args) >= 2:
            key_ann, value_ann = args[0], args[1]
            # For simplicity, we'll assume keys are strings for mapping types
            value_schema = _annotation_to_schema(value_ann)
            return {"type": "object", "additionalProperties": value_schema}
        else:
            # Fallback to generic object with additional properties
            return {"type": "object", "additionalProperties": {"type": "string"}}

    # Tuple
    if origin is tuple or (origin and hasattr(origin, '__tuple_params__')):
        args = get_args(ann)
        if args:
            items_schema = [_annotation_to_schema(arg) for arg in args]
            return {
                "type": "array",
                "items": items_schema,
                "minItems": len(items_schema),
                "maxItems": len(items_schema),
            }

    # Fallbacks
    if ann is typing.Any or ann is object:
        return {}  # unconstrained

    # Unknown - fallback to string
    return {"type": "string"}


def function_to_openai_tool(
    fn,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """
    Build an OpenAI function/tool schema from a Python callable.
    Prefer parameter descriptions from the docstring; otherwise rely on signature.
    Functions with no parameters produce an empty 'properties' and no 'required'.
    """
    if not callable(fn):
        raise TypeError("fn must be callable")

    sig = inspect.signature(fn)
    doc = inspect.getdoc(fn) or ""
    name = name or fn.__name__
    description = description or _first_line(doc)
    param_descs = _parse_doc_params(doc)

    properties = {}
    required = []
    stateless = True
    for pname, param in sig.parameters.items():
        # Skip typical self/cls for methods
        if pname in ("self", "cls"):
            continue
        if pname == "context":
            stateless = False
            continue

        if param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            # *args / **kwargs are not representable in OpenAI function schemas; skip them
            continue

        ann = param.annotation
        schema = _annotation_to_schema(ann)

        # Description priority: docstring description > parameter annotation > default
        desc = param_descs.get(pname)
        if desc:
            schema["description"] = desc

        properties[pname] = schema

        # Required parameters (no default value or default is None for optional args)
        if param.default is inspect.Parameter.empty and not (ann is not None and ann != inspect._empty):
            required.append(pname)

    parameters: dict = {"type": "object", "properties": properties}
    if required:
        parameters["required"] = required

    # Ensure empty object when no params
    if not properties:
        parameters = {"type": "object", "properties": {}}

    return (
        {
            "type": "function",
            "function": {
                "name": name,
                "description": description or name.replace("_", " ").title(),
                "parameters": parameters,
            },
        },
        stateless,
    )


Target = Union[Callable, type]


def tool(
    *args,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Callable[[Callable], Callable]:
    """
    Decorator that parses the target function's docstring and attaches
    an OpenAI tool schema as `__openai_tool_schema__`.
    You can override name/description if desired.
    """
    def _decorator(func: Callable) -> Callable:
        schema, stateless = function_to_openai_tool(func)
        if name:
            schema["function"]["name"] = name
        if description:
            schema["function"]["description"] = description
        setattr(func, "__openai_tool_schema__", schema)
        setattr(func, "__tool_stateless__", stateless)
        return func

    if len(args) == 1 and callable(args[0]):
        # Used as @tool (without parentheses)
        return _decorator(args[0])
    else:
        # Used as @tool(...) with arguments
        return _decorator


def discover_tools(
    funcs: List[Union[Callable, Dict[str, Any]]],
) -> Tuple[List[Dict[str, Any]], Dict[str, Tuple[Callable, bool]]]:
    """
    Collect attached schemas from decorated functions.
    
    Returns:
        tuple: (tool_metas, tools_mapping)
            - tool_metas: list of OpenAI function schemas
            - tools_mapping: dict mapping tool names to (function, is_stateless) tuples
    """
    tool_metas = []
    tools_mapping = {}
    for f in funcs:
        if isinstance(f, dict):
            # Predefined tool schema
            tool_metas.append(f)
            continue
        schema = getattr(f, "__openai_tool_schema__", None)
        stateless = None
        if not schema:
            schema, stateless = function_to_openai_tool(f)

        if schema:
            stateless = (
                stateless
                if stateless is not None
                else getattr(f, "__tool_stateless__", True)
            )
            tools_mapping[schema["function"]["name"]] = (f, stateless)
            tool_metas.append(schema)

    return tool_metas, tools_mapping