"""JSON formatting utilities for screen output."""

import re
from typing import Dict


def align_json_colons(json_str: str) -> str:
    """Align colons in JSON output for better readability (screen output only).
    
    Takes a JSON string (from json.dumps) and aligns all colons vertically
    at each indentation level for improved visual readability.
    
    Args:
        json_str: JSON string to format
        
    Returns:
        Formatted JSON string with aligned colons
    """
    lines = json_str.split("\n")
    if len(lines) <= 1:
        return json_str
    
    # Find lines with key-value pairs (contain ": ")
    key_lines = []
    for i, line in enumerate(lines):
        # Match lines like: '  "key": value,'
        match = re.match(r'^(\s+)"([^"]+)":\s+(.+)$', line)
        if match:
            indent, key, value = match.groups()
            key_lines.append((i, len(indent), len(key), line))
    
    if not key_lines:
        return json_str
    
    # Find max key length at each indentation level
    max_key_len_by_indent: Dict[int, int] = {}
    for _, indent_len, key_len, _ in key_lines:
        if indent_len not in max_key_len_by_indent:
            max_key_len_by_indent[indent_len] = key_len
        else:
            max_key_len_by_indent[indent_len] = max(max_key_len_by_indent[indent_len], key_len)
    
    # Rebuild lines with aligned colons
    result_lines = []
    for i, line in enumerate(lines):
        match = re.match(r'^(\s+)"([^"]+)":\s+(.+)$', line)
        if match:
            indent, key, value = match.groups()
            indent_len = len(indent)
            max_key_len = max_key_len_by_indent.get(indent_len, len(key))
            padding = " " * (max_key_len - len(key))
            result_lines.append(f'{indent}{padding}"{key}": {value}')
        else:
            result_lines.append(line)
    
    return "\n".join(result_lines)

