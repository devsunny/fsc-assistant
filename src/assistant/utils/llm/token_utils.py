import json
from typing import Any, Dict, Iterable, List, Optional

# Optional dependency: tiktoken (OpenAI tokenization)
# Fallback: approximate tokens by characters/4 when tiktoken is not available
try:
    import tiktoken  # type: ignore
except Exception:  # pragma: no cover
    tiktoken = None  # type: ignore


def _get_encoding(model: Optional[str] = None):
    """
    Return a tiktoken encoding for the given model or a default encoding.
    If tiktoken is unavailable, return None and use the fallback.
    """
    if tiktoken is None:
        return None
    try:
        if model:
            return tiktoken.encoding_for_model(model)
        # Default that works for most GPT-3.5/4 class models
        return tiktoken.get_encoding("o200k_base")
    except Exception:
        return tiktoken.get_encoding("cl100k_base")


def _count_tokens_text(text: str, model: Optional[str] = None) -> int:
    """
    Count tokens in a single text string using tiktoken if available, otherwise
    a simple approximation based on characters.
    """
    if not text:
        return 0
    enc = _get_encoding(model)
    if enc is not None:
        try:
            return len(enc.encode(text))
        except Exception:
            # Fallback to approximate if encoding fails
            pass
    # Approximate: avg ~4 chars per token for English
    return max(1, len(text) // 4)


def _normalize_content(content: Any) -> str:
    """
    Normalize a message content field to a text string.
    Supports:
    - None: returns ""
    - str: returns as-is
    - list[dict]: extracts text from entries with type == 'text' or 'input_text',
      otherwise JSON-serializes non-text parts
    - dict: JSON-serialize
    - other: str() fallback
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, dict):
                t = item.get("text") or item.get("input_text")
                if isinstance(t, str):
                    parts.append(t)
                else:
                    # Non-text (images/audio/etc.) contribute minimally to tokens
                    parts.append(json.dumps(item, ensure_ascii=False))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    if isinstance(content, dict):
        return json.dumps(content, ensure_ascii=False)
    return str(content)


def _normalize_tool_calls(tool_calls: Any) -> str:
    """
    Normalize tool_calls field to text for token counting.
    Supports str, dict, list -> JSON string. None -> "".
    """
    if tool_calls is None:
        return ""
    if isinstance(tool_calls, str):
        return tool_calls
    try:
        return json.dumps(tool_calls, ensure_ascii=False)
    except Exception:
        return str(tool_calls)


def count_message_tokens(message: Dict[str, Any], model: Optional[str] = None) -> int:
    """
    Count tokens for a single chat message.
    Considers 'content', 'tool_calls', 'function_call', and optional 'name'.

    Args:
        message: Chat message dict, e.g., {"role": "assistant", "content": None, "tool_calls": [...]}
        model: Optional model name to select tokenizer (e.g., 'gpt-4o-mini', 'gpt-4-turbo').

    Returns:
        int: token count for the message.
    """
    tokens = 0

    # Role contributes a tiny amount in ChatML; include for completeness
    role = message.get("role")
    if isinstance(role, str):
        tokens += _count_tokens_text(role, model)

    # Content
    tokens += _count_tokens_text(_normalize_content(message.get("content")), model)

    # Tool calls (OpenAI responses)
    tokens += _count_tokens_text(
        _normalize_tool_calls(message.get("tool_calls")), model
    )

    # Legacy function_call field
    tokens += _count_tokens_text(
        _normalize_tool_calls(message.get("function_call")), model
    )

    # Optional name field (system/tool messages)
    name = message.get("name")
    if isinstance(name, str):
        tokens += _count_tokens_text(name, model)

    # Optional tool_call_id (assistants API)
    tool_call_id = message.get("tool_call_id")
    if isinstance(tool_call_id, str):
        tokens += _count_tokens_text(tool_call_id, model)

    return tokens


def total_llm_tokens(
    messages: Iterable[Dict[str, Any]], model: Optional[str] = None
) -> int:
    """
    Calculate the total number of LLM tokens across a list/iterable of messages.

    Args:
        messages: Iterable of chat messages. Each message may have fields like 'role', 'content', 'tool_calls'.
        model: Optional model name to select tokenizer. If None, uses default encoding or heuristic.

    Returns:
        Total token count as an integer.

    Notes:
        - This counts tokens in the message fields themselves. Different model/chat formats may add
          extra per-message or per-request overhead not accounted here.
        - For precise accounting per model (including ChatML overhead), integrate model-specific rules
          if needed.
    """
    total = 0
    for msg in messages:
        try:
            total += count_message_tokens(msg, model)
        except Exception:
            # Be resilient to malformed messages
            continue
    return total


__all__ = [
    "count_message_tokens",
    "total_llm_tokens",
]
