from __future__ import annotations

import re


__all__ = (
    "routing_part_regex",
    "is_valid_routing_part",
    "validate_routing_part",
)


routing_part_regex = r"^[a-zA-Z0-9_-]+$"


def is_valid_routing_part(value: str) -> bool:
    return bool(re.match(routing_part_regex, value))


def validate_routing_part(value: str):
    if not is_valid_routing_part(value):
        raise ValueError("contains invalid character")
