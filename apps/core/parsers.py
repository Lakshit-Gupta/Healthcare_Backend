"""orjson-based DRF parser."""

from collections.abc import Mapping
from typing import Any

import orjson
from django.conf import settings
from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser


class ORJSONParser(BaseParser):
    """High-performance JSON parser using orjson."""

    media_type = "application/json"

    def parse(
        self,
        stream: Any,
        media_type: str | None = None,
        parser_context: Mapping[str, Any] | None = None,
    ) -> Any:
        try:
            encoding = (
                parser_context.get("encoding", settings.DEFAULT_CHARSET)
                if parser_context
                else "utf-8"
            )
            return orjson.loads(stream.read().decode(encoding))
        except orjson.JSONDecodeError as exc:
            raise ParseError(f"JSON parse error: {exc}") from exc
