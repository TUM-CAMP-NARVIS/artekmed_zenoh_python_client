from __future__ import annotations
from dataclasses import dataclass
from numpy import uint8, uint64

from .model import (
    constants,
    EmptyCustomType,
    EmptyMaskType,
    GenericCompressionTypes,
    GenericFormatTypes,
)


@dataclass
class GenericContentConfig:
    compression_type: GenericCompressionTypes | None = None
    format_type: GenericFormatTypes | None = None
    custom1_type: EmptyCustomType | None = None
    custom2_type: EmptyCustomType | None = None
    custom_mask_type: EmptyMaskType | None = None

    @classmethod
    def new(cls, value: uint64) -> "GenericContentConfig":
        cfg = cls()
        cfg.compression_type = GenericCompressionTypes.from_u8(
            ((uint64(value) & uint64(constants.COMPRESSION_TYPE_MASK)) >> uint8(constants.COMPRESSION_TYPE_OFFSET))
        )
        cfg.format_type = GenericFormatTypes.from_u8(
            ((uint64(value) & uint64(constants.FORMAT_TYPE_MASK)) >> uint8(constants.FORMAT_TYPE_OFFSET))
        )
        cfg.custom1_type = EmptyCustomType.from_u8(
            ((uint64(value) & uint64(constants.CUSTOM1_TYPE_MASK)) >> uint8(constants.CUSTOM1_TYPE_OFFSET))
        )
        cfg.custom2_type = EmptyCustomType.from_u8(
            ((uint64(value) & uint64(constants.CUSTOM2_TYPE_MASK)) >> uint8(constants.CUSTOM2_TYPE_OFFSET))
        )
        cfg.custom_mask_type = EmptyMaskType.from_u8(
            ((uint64(value) & uint64(constants.CUSTOM_MASK_TYPE_MASK)) >> uint8(constants.CUSTOM_MASK_TYPE_OFFSET))
        )
        return cfg

    @classmethod
    def default(cls) -> "GenericContentConfig":
        return cls.new(uint64(0))

    @classmethod
    def from_u64(cls, value: uint64) -> "GenericContentConfig":
        return cls.new(value)

    def to_u64(self) -> uint64:
        value = uint64(0)
        if self.compression_type is not None:
            value |= uint64(self.compression_type.as_u8()) << constants.COMPRESSION_TYPE_OFFSET
        if self.format_type is not None:
            value |= uint64(self.format_type.as_u8()) << constants.FORMAT_TYPE_OFFSET
        if self.custom1_type is not None:
            value |= uint64(self.custom1_type.as_u8()) << constants.CUSTOM1_TYPE_OFFSET
        if self.custom2_type is not None:
            value |= uint64(self.custom2_type.as_u8()) << constants.CUSTOM2_TYPE_OFFSET
        if self.custom_mask_type is not None:
            value |= uint64(self.custom_mask_type.as_u8()) << constants.CUSTOM_MASK_TYPE_OFFSET
        return value

    # Getters
    def get_compression_type(self) -> GenericCompressionTypes | None:
        return self.compression_type

    def get_format_type(self) -> GenericFormatTypes | None:
        return self.format_type

    def get_custom1_type(self) -> EmptyCustomType | None:
        return self.custom1_type

    def get_custom2_type(self) -> EmptyCustomType | None:
        return self.custom2_type

    def get_custom_mask_type(self) -> EmptyMaskType | None:
        return self.custom_mask_type

    # Setters
    def set_compression_type(self, compression_type: GenericCompressionTypes) -> None:
        self.compression_type = compression_type

    def set_format_type(self, format_type: GenericFormatTypes) -> None:
        self.format_type = format_type

    def set_custom1_type(self, custom1_type: EmptyCustomType) -> None:
        self.custom1_type = custom1_type

    def set_custom2_type(self, custom2_type: EmptyCustomType) -> None:
        self.custom2_type = custom2_type

    def set_custom_mask_type(self, mask_type: EmptyMaskType) -> None:
        self.custom_mask_type = mask_type
