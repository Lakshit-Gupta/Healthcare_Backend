"""orjson-based DRF renderer."""

from collections.abc import Mapping
from typing import Any

import orjson
from rest_framework.renderers import BaseRenderer


class ORJSONRenderer(BaseRenderer):
    """High-performance JSON renderer using orjson."""

    media_type = "application/json"
    format = "json"

    def render(
        self,
        data: object,
        accepted_media_type: str | None = None,
        renderer_context: Mapping[str, Any] | None = None,
    ) -> bytes:
        if data is None:
            return b""
        return orjson.dumps(
            data,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_UUID,
        )
