from typing import Any

import requests

from flythings.schemas import JsonValue


def json_or_text(response: requests.Response) -> JsonValue:
    """Decoded JSON body, the raw text when it is not JSON, or `None` when the body is empty.

    For endpoints whose answer is not documented, so a plain-text answer is returned instead of failing.
    """
    if not response.content:
        return None
    try:
        return response.json()
    except ValueError:
        return response.text


def json_or_none(response: requests.Response) -> Any:
    """Decoded JSON body, or `None` when the body is empty. Raises `ValueError` when the body is not JSON.

    For endpoints whose answer has a known shape (a `TypedDict`), so text is never returned in its place.
    """
    return response.json() if response.content else None
