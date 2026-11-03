"""Custom msgspec payload converter for Temporal.io serialization."""

import dataclasses
from typing import Any

import msgspec
from temporalio.api.common.v1 import Payload
from temporalio.converter import (
    CompositePayloadConverter,
    DataConverter,
    DefaultPayloadConverter,
    EncodingPayloadConverter,
)


class MsgspecEncodingPayloadConverter(EncodingPayloadConverter):
    """Payload converter that serializes and deserializes msgspec.Struct instances."""

    @property
    def encoding(self) -> str:
        return "application/x-msgspec-json"

    def to_payload(self, value: Any) -> Payload | None:
        if isinstance(value, msgspec.Struct):
            return Payload(
                metadata={
                    "encoding": self.encoding.encode(),
                    "messageType": f"{type(value).__module__}.{type(value).__qualname__}".encode(),
                },
                data=msgspec.json.encode(value),
            )
        return None

    def from_payload(self, payload: Payload, type_hint: type | None = None) -> Any:
        if type_hint and isinstance(type_hint, type) and issubclass(type_hint, msgspec.Struct):
            return msgspec.json.decode(payload.data, type=type_hint)
        return msgspec.json.decode(payload.data)


class OjasOpsPayloadConverter(CompositePayloadConverter):
    """Composite payload converter prioritizing native msgspec serialization."""

    def __init__(self) -> None:
        super().__init__(
            MsgspecEncodingPayloadConverter(),
            *DefaultPayloadConverter.default_encoding_payload_converters,
        )


def get_ojas_ops_data_converter() -> DataConverter:
    """Returns a DataConverter using OjasOpsPayloadConverter."""
    import temporalio.converter

    return dataclasses.replace(
        temporalio.converter.default(),
        payload_converter_class=OjasOpsPayloadConverter,
    )
