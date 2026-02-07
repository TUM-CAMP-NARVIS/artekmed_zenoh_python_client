from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Union
from numpy import uint8, uint32, uint64

from . import model
from .generic import GenericContentConfig
from .image import ImageContentConfig
from .geometry import GeometryContentConfig
from .transform import TransformContentConfig

from .model import (
    BaseIdentifierStorageType,
    IdentifierStorageType,
    ScalarType,
    CardinalityType,
    ContainerType,
    MemoryRepresentationType,
    ContentTypes,
    constants,
)

__all__ = [
    "model",
    "GenericContentConfig",
    "ImageContentConfig",
    "GeometryContentConfig",
    "TransformContentConfig",
    "SemanticType",
    "BaseIdentifierStorageType",
    "IdentifierStorageType",
    "ScalarType",
    "CardinalityType",
    "ContainerType",
    "MemoryRepresentationType",
    "ContentTypes",
    "constants",
]


# python




def combine_flags(flags: List[uint64]) -> uint64:
    acc = 0
    for flag in flags:
        acc |= flag
    return acc


@dataclass(frozen=True)
class InvalidContentConfig:
    pass


ContentTypeConfigStorage = Union[
    InvalidContentConfig,
    GenericContentConfig,
    ImageContentConfig,
    GeometryContentConfig,
    TransformContentConfig,
]


def get_content_type(value: uint64) -> Optional[ContentTypes]:
    ct_u8 = (value & constants.CONTENT_TYPE_MASK) >> constants.CONTENT_TYPE_OFFSET
    return ContentTypes.from_u8(ct_u8) or ContentTypes.None_


def set_content_type(content_type: ContentTypes) -> uint64:
    return (content_type.as_u8() & 0xFF) << constants.CONTENT_TYPE_OFFSET


def _content_storage_to_u64(cfg: ContentTypeConfigStorage) -> uint64:
    if isinstance(cfg, GenericContentConfig):
        return cfg.to_u64()
    if isinstance(cfg, ImageContentConfig):
        return cfg.to_u64()
    if isinstance(cfg, GeometryContentConfig):
        return cfg.to_u64()
    if isinstance(cfg, TransformContentConfig):
        return cfg.to_u64()
    return uint64(0)


def _content_storage_to_type(cfg: ContentTypeConfigStorage) -> ContentTypes:
    if isinstance(cfg, GenericContentConfig):
        return ContentTypes.Generic
    if isinstance(cfg, ImageContentConfig):
        return ContentTypes.Image
    if isinstance(cfg, GeometryContentConfig):
        return ContentTypes.Geometry
    if isinstance(cfg, TransformContentConfig):
        return ContentTypes.Transform
    return ContentTypes.None_


def _content_from_type_and_id(ct: ContentTypes, semantic_bits: uint32) -> ContentTypeConfigStorage:
    masked = uint32(semantic_bits) & uint32(constants.SEMANTIC_TYPE_MASK)
    if ct == ContentTypes.Generic:
        return GenericContentConfig.from_u64(masked)
    if ct == ContentTypes.Image:
        return ImageContentConfig.from_u64(masked)
    if ct == ContentTypes.Geometry:
        return GeometryContentConfig.from_u64(masked)
    if ct == ContentTypes.Transform:
        return TransformContentConfig.from_u64(masked)
    return InvalidContentConfig()


@dataclass
class BaseType:
    scalar_type: Optional[ScalarType] = ScalarType.None_
    cardinality_type: Optional[CardinalityType] = CardinalityType.None_
    container_type: Optional[ContainerType] = ContainerType.None_
    memory_representation_type: Optional[MemoryRepresentationType] = MemoryRepresentationType.None_

    @staticmethod
    def from_identifier(value: BaseIdentifierStorageType) -> "BaseType":
        st = uint64(uint64(value) & uint64(constants.SCALAR_TYPE_MASK)) >> uint8(constants.SCALAR_TYPE_OFFSET)
        cat = uint64(uint64(value) & uint64(constants.CARDINALITY_TYPE_MASK)) >> uint8(constants.CARDINALITY_TYPE_OFFSET)
        ct = uint64(uint64(value) & uint64(constants.CONTAINER_TYPE_MASK)) >> uint8(constants.CONTAINER_TYPE_OFFSET)
        mrt = uint64(uint64(value) & uint64(constants.MEMORY_REPRESENTATION_TYPE_MASK)) >> uint8(constants.MEMORY_REPRESENTATION_TYPE_OFFSET)
        return BaseType(
            scalar_type=ScalarType.from_u8(st) or ScalarType.None_,
            cardinality_type=CardinalityType.from_u8(cat) or CardinalityType.None_,
            container_type=ContainerType.from_u8(ct) or ContainerType.None_,
            memory_representation_type=MemoryRepresentationType.from_u8(mrt) or MemoryRepresentationType.None_,
        )

    @staticmethod
    def create(
        st: ScalarType,
        cat: CardinalityType,
        ct: ContainerType,
        mrt: MemoryRepresentationType,
    ) -> "BaseType":
        return BaseType(st, cat, ct, mrt)

    def base_type_identifier(self) -> BaseIdentifierStorageType:
        st_value = uint64(self.scalar_type.as_u8() & uint8(0x3F)) << uint8(constants.SCALAR_TYPE_OFFSET)
        cat_value = uint64(self.cardinality_type.as_u8() & uint8(0x03)) << uint8(constants.CARDINALITY_TYPE_OFFSET)
        ct_value = uint64(self.container_type.as_u8() & uint8(0x3F)) << uint8(constants.CONTAINER_TYPE_OFFSET)
        mrt_value = uint64(self.memory_representation_type.as_u8() & uint8(0x03)) << uint8(constants.MEMORY_REPRESENTATION_TYPE_OFFSET)
        return uint32(st_value | cat_value | ct_value | mrt_value)

    def is_compatible(self, value: uint32) -> bool:
        other = BaseType.from_identifier(value)

        def enum_match_query(a, b, match_value) -> bool:
            if match_value == a.__class__.Match:  # treat MATCH semantics
                return a == b
            # If "None" means wildcard, accept any
            none_map = {
                ScalarType: ScalarType.None_,
                MemoryRepresentationType: MemoryRepresentationType.None_,
                ContainerType: ContainerType.None_,
                CardinalityType: CardinalityType.None_,
            }
            none_value = none_map[a.__class__]
            if a == none_value or b == none_value:
                return True
            # Same tag equals compatible
            return a.as_u8() == b.as_u8()

        return (
            enum_match_query(self.scalar_type, other.scalar_type, ScalarType.Match)
            and enum_match_query(self.memory_representation_type, other.memory_representation_type, MemoryRepresentationType.Match)
            and enum_match_query(self.container_type, other.container_type, ContainerType.Match)
            and enum_match_query(self.cardinality_type, other.cardinality_type, CardinalityType.Match)
        )


class SemanticType:
    def __init__(self, semantic_type_id: IdentifierStorageType | None = None):
        if semantic_type_id is None:
            self.base_type = BaseType()
            self.content_type: ContentTypeConfigStorage = InvalidContentConfig()
        else:
            base_bits = uint64(semantic_type_id) & uint64(constants.BASE_TYPE_MASK)
            self.base_type = BaseType.from_identifier(base_bits)
            ct = get_content_type(semantic_type_id)
            self.content_type = _content_from_type_and_id(ct, uint64(semantic_type_id))

    @staticmethod
    def new(semantic_type_id: IdentifierStorageType) -> "SemanticType":
        return SemanticType(semantic_type_id)

    @staticmethod
    def default() -> "SemanticType":
        return SemanticType(None)

    @staticmethod
    def from_identifier(value: IdentifierStorageType) -> "SemanticType":
        return SemanticType(value)

    def to_identifier(self) -> IdentifierStorageType:
        content_bits = _content_storage_to_u64(self.content_type) & uint64(constants.SEMANTIC_TYPE_MASK)
        base_bits = self.base_type.base_type_identifier() & uint64(constants.BASE_TYPE_MASK)
        # Ensure content type tag is set consistently with stored config
        content_bits |= set_content_type(_content_storage_to_type(self.content_type))
        return uint64((content_bits | base_bits) & uint64(0xFFFFFFFFFFFFFFFF))

    # BaseType proxied getters/setters
    def scalar_type(self) -> ScalarType:
        return self.base_type.scalar_type

    def set_scalar_type(self, scalar_type: ScalarType) -> None:
        self.base_type.scalar_type = scalar_type

    def cardinality_type(self) -> CardinalityType:
        return self.base_type.cardinality_type

    def set_cardinality_type(self, cardinality_type: CardinalityType) -> None:
        self.base_type.cardinality_type = cardinality_type

    def container_type(self) -> ContainerType:
        return self.base_type.container_type

    def set_container_type(self, container_type: ContainerType) -> None:
        self.base_type.container_type = container_type

    def memory_representation_type(self) -> MemoryRepresentationType:
        return self.base_type.memory_representation_type

    def set_memory_representation_type(self, memory_representation_type: MemoryRepresentationType) -> None:
        self.base_type.memory_representation_type = memory_representation_type

    def set_content_type(self, ct: ContentTypes, config: Optional[int]) -> None:
        semantic_bits = (config or 0) & uint64(constants.SEMANTIC_TYPE_MASK)
        self.content_type = _content_from_type_and_id(ct, semantic_bits)

    def get_content_type(self) -> ContentTypeConfigStorage:
        return self.content_type

    # Pretty print similar to Rust Debug impl
    def __repr__(self) -> str:
        value = self.to_identifier()
        base_part = value & uint64(constants.BASE_TYPE_MASK)

        st = (base_part & uint64(constants.SCALAR_TYPE_MASK)) >> uint8(constants.SCALAR_TYPE_OFFSET)
        cat = (base_part & uint64(constants.CARDINALITY_TYPE_MASK)) >> uint8(constants.CARDINALITY_TYPE_OFFSET)
        ct = (base_part & uint64(constants.CONTAINER_TYPE_MASK)) >> uint8(constants.CONTAINER_TYPE_OFFSET)
        mrt = (base_part & uint64(constants.MEMORY_REPRESENTATION_TYPE_MASK)) >> uint8(constants.MEMORY_REPRESENTATION_TYPE_OFFSET)

        scalar_name = (ScalarType.from_u8(st) or ScalarType.None_).name_str()
        cardinality_name = (CardinalityType.from_u8(cat) or CardinalityType.None_).name_str()
        container_name = (ContainerType.from_u8(ct) or ContainerType.None_).name_str()
        memory_name = (MemoryRepresentationType.from_u8(mrt) or MemoryRepresentationType.None_).name_str()
        content_type_name = _content_storage_to_type(self.content_type).name_str()

        compression = ""
        fmt = ""
        custom1 = ""
        custom2 = ""
        mask = ""

        try:
            if isinstance(self.content_type, (GenericContentConfig, ImageContentConfig, TransformContentConfig)):
                compression = (self.content_type.get_compression_type().name_str())  # type: ignore[attr-defined]
                fmt = (self.content_type.get_format_type().name_str())  # type: ignore[attr-defined]
                custom1 = (self.content_type.get_custom1_type().name_str())  # type: ignore[attr-defined]
                custom2 = (self.content_type.get_custom2_type().name_str())  # type: ignore[attr-defined]
                mask = (self.content_type.get_custom_mask_type().name_str())  # type: ignore[attr-defined]
            elif isinstance(self.content_type, GeometryContentConfig):
                compression = self.content_type.get_compression_type().name_str()  # type: ignore[attr-defined]
                fmt = self.content_type.get_format_type().name_str()  # type: ignore[attr-defined]
                custom1 = self.content_type.get_custom1_type().name_str()  # type: ignore[attr-defined]
                custom2 = self.content_type.get_custom2_type().name_str()  # type: ignore[attr-defined]
                # geometry mask may already be a string or enum; standardize
                mask_v = self.content_type.get_custom_mask_type()  # type: ignore[attr-defined]
                mask = mask_v.name_str() if hasattr(mask_v, "name_str") else str(mask_v)
        except Exception as e:
            pass

        return (
            "SemanticType("
            f"scalar='{scalar_name}', "
            f"cardinality='{cardinality_name}', "
            f"container='{container_name}', "
            f"memory_representation='{memory_name}', "
            f"content='{content_type_name}', "
            f"compression='{compression}', "
            f"format='{fmt}', "
            f"custom1='{custom1}', "
            f"custom2='{custom2}', "
            f"custom_mask='{mask}'"
            ")"
        )