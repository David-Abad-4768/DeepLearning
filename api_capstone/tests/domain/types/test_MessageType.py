import pytest

from app.domain.types.MessageType import MessageTypeEnum


def test_enum_members():
    assert list(MessageTypeEnum.__members__.keys()) == ["SYSTEM", "CLIENT"]
    assert hasattr(MessageTypeEnum, "SYSTEM")
    assert hasattr(MessageTypeEnum, "CLIENT")


def test_enum_values():
    assert MessageTypeEnum.SYSTEM.value == "system"
    assert MessageTypeEnum.CLIENT.value == "client"


def test_enum_lookup_by_value():
    assert MessageTypeEnum("system") is MessageTypeEnum.SYSTEM
    assert MessageTypeEnum("client") is MessageTypeEnum.CLIENT


def test_enum_length():
    assert len(list(MessageTypeEnum)) == 2
