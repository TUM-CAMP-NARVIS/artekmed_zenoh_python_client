from __future__ import annotations
from enum import Enum
from numpy import uint64, uint32, uint16, uint8

# Type aliases for clarity (not strictly necessary in Python)
BaseIdentifierStorageType = uint32
IdentifierStorageType = uint64


class constants:
    SCALAR_TYPE_OFFSET: int = int(0)
    CARDINALITY_TYPE_OFFSET: int = int(6)
    CONTAINER_TYPE_OFFSET: int = int(8)
    MEMORY_REPRESENTATION_TYPE_OFFSET: int = int(14)

    SCALAR_TYPE_MASK: uint64 = uint64(0x3F << SCALAR_TYPE_OFFSET)
    CARDINALITY_TYPE_MASK: uint64 = uint64(0x03 << CARDINALITY_TYPE_OFFSET)
    CONTAINER_TYPE_MASK: uint64 = uint64(0x3F << CONTAINER_TYPE_OFFSET)
    MEMORY_REPRESENTATION_TYPE_MASK: uint64 = uint64(0x03 << MEMORY_REPRESENTATION_TYPE_OFFSET)

    CONTENT_TYPE_OFFSET: int = int(16)
    COMPRESSION_TYPE_OFFSET: int = int(24)
    FORMAT_TYPE_OFFSET: int = int(32)
    CUSTOM1_TYPE_OFFSET: int = int(40)
    CUSTOM2_TYPE_OFFSET: int = int(48)
    CUSTOM_MASK_TYPE_OFFSET: int = int(56)

    BASE_TYPE_MASK: uint64 = uint64(0xFFFF)
    SEMANTIC_TYPE_MASK: uint64 = uint64((~BASE_TYPE_MASK) & 0xFFFFFFFFFFFFFFFF)
    CONTENT_TYPE_MASK: uint64 = uint64(0xFF << CONTENT_TYPE_OFFSET)
    COMPRESSION_TYPE_MASK: uint64 = uint64(0xFF << COMPRESSION_TYPE_OFFSET)
    FORMAT_TYPE_MASK: uint64 = uint64(0xFF << FORMAT_TYPE_OFFSET)
    CUSTOM1_TYPE_MASK: uint64 = uint64(0xFF << CUSTOM1_TYPE_OFFSET)
    CUSTOM2_TYPE_MASK: uint64 = uint64(0xFF << CUSTOM2_TYPE_OFFSET)
    CUSTOM_MASK_TYPE_MASK: uint64 = uint64(0xFF << CUSTOM_MASK_TYPE_OFFSET)


# Utilities similar to SemanticTypeEnum behavior in Rust
class _SemanticHelpers:
    @staticmethod
    def is_none(value: Enum, none_value: Enum) -> bool:
        return value == none_value

    @staticmethod
    def is_match(value: Enum, match_value: Enum) -> bool:
        return value == match_value


# BaseType enums
class ScalarType(Enum):
    None_ = 0x00
    Bool = 0x01
    Char = 0x02
    UChar = 0x03
    WChar = 0x04
    Int16 = 0x05
    Int32 = 0x06
    Int64 = 0x07
    UInt16 = 0x08
    UInt32 = 0x09
    UInt64 = 0x0A
    Float32 = 0x0B
    Float64 = 0x0C
    Complex32 = 0x0D
    Complex64 = 0x0E
    Match = 0x3F

    def name_str(self) -> str:
        mapping = {
            ScalarType.None_: "NONE",
            ScalarType.Bool: "BOOL",
            ScalarType.Char: "CHAR",
            ScalarType.UChar: "UCHAR",
            ScalarType.WChar: "WCHAR",
            ScalarType.Int16: "INT16",
            ScalarType.Int32: "INT32",
            ScalarType.Int64: "INT64",
            ScalarType.UInt16: "UINT16",
            ScalarType.UInt32: "UINT32",
            ScalarType.UInt64: "UINT64",
            ScalarType.Float32: "FLOAT32",
            ScalarType.Float64: "FLOAT64",
            ScalarType.Complex32: "COMPLEX32",
            ScalarType.Complex64: "COMPLEX64",
            ScalarType.Match: "MATCH",
        }
        return mapping[self]

    @staticmethod
    def from_u8(value: uint8) -> ScalarType | None:
        try:
            return ScalarType(value)
        except ValueError:
            return None

    def as_u8(self) -> uint8:
        return uint8(self.value)


class CardinalityType(Enum):
    None_ = 0x00
    Fixed = 0x01
    Variable = 0x02
    Match = 0x03

    def name_str(self) -> str:
        return {
            CardinalityType.None_: "NONE",
            CardinalityType.Fixed: "FIXED",
            CardinalityType.Variable: "VARIABLE",
            CardinalityType.Match: "MATCH",
        }[self]

    @staticmethod
    def from_u8(value: uint8) -> CardinalityType | None:
        try:
            return CardinalityType(value)
        except ValueError:
            return None

    def as_u8(self) -> uint8:
        return uint8(self.value)


class ContainerType(Enum):
    None_ = 0x00
    Scalar = 0x01
    Array1D = 0x02
    Array2D = 0x03
    Array3D = 0x04
    Array4D = 0x05
    Match = 0x3F

    def name_str(self) -> str:
        return {
            ContainerType.None_: "NONE",
            ContainerType.Scalar: "SCALAR",
            ContainerType.Array1D: "ARRAY1D",
            ContainerType.Array2D: "ARRAY2D",
            ContainerType.Array3D: "ARRAY3D",
            ContainerType.Array4D: "ARRAY4D",
            ContainerType.Match: "MATCH",
        }[self]

    @staticmethod
    def from_u8(value: uint8) -> ContainerType | None:
        try:
            return ContainerType(value)
        except ValueError:
            return None

    def as_u8(self) -> uint8:
        return uint8(self.value)

    def dimensions(self) -> int | None:
        return {
            ContainerType.Scalar: 0,
            ContainerType.Array1D: 1,
            ContainerType.Array2D: 2,
            ContainerType.Array3D: 3,
            ContainerType.Array4D: 4,
        }.get(self)


class MemoryRepresentationType(Enum):
    None_ = 0x00
    Raw = 0x01
    Compressed = 0x02
    Match = 0x03

    def name_str(self) -> str:
        return {
            MemoryRepresentationType.None_: "NONE",
            MemoryRepresentationType.Raw: "RAW",
            MemoryRepresentationType.Compressed: "COMPRESSED",
            MemoryRepresentationType.Match: "MATCH",
        }[self]

    def as_u8(self) -> uint8:
        return uint8(self.value)

    @staticmethod
    def from_u8(value: uint8) -> MemoryRepresentationType | None:
        try:
            return MemoryRepresentationType(value)
        except ValueError:
            return None


# Content types
class ContentTypes(Enum):
    None_ = 0x00
    Generic = 0x01
    Image = 0x02
    Geometry = 0x03
    Transform = 0x04
    Match = 0xFF

    def name_str(self) -> str:
        return {
            ContentTypes.None_: "None",
            ContentTypes.Generic: "Generic",
            ContentTypes.Image: "Image",
            ContentTypes.Geometry: "Geometry",
            ContentTypes.Transform: "Transform",
            ContentTypes.Match: "Match",
        }[self]

    def as_u8(self) -> uint8:
        return uint8(self.value)

    @staticmethod
    def from_u8(value: uint8) -> ContentTypes | None:
        try:
            return ContentTypes(value)
        except ValueError:
            return None


# Generic
class GenericFormatTypes(Enum):
    None_ = 0x00
    Raw = 0x01
    Custom = 0x02
    Match = 0xFF

    def as_u8(self) -> uint8: return uint8(self.value)

    @staticmethod
    def from_u8(value: uint8) -> GenericFormatTypes | None:
        try:
            return GenericFormatTypes(value)
        except ValueError:
            return None

    def name_str(self) -> str:
        return {
            GenericFormatTypes.None_: "None",
            GenericFormatTypes.Raw: "Raw",
            GenericFormatTypes.Custom: "Custom",
            GenericFormatTypes.Match: "Match",
        }[self]


class GenericCompressionTypes(Enum):
    None_ = 0x00
    Uncompressed = 0x01
    Zstd = 0x02
    Zip = 0x03
    Bzip = 0x04
    Match = 0xFF

    def as_u8(self) -> uint8: return uint8(self.value)

    @staticmethod
    def from_u8(value: uint8) -> GenericCompressionTypes | None:
        try:
            return GenericCompressionTypes(value)
        except ValueError:
            return None

    def name_str(self) -> str:
        return {
            GenericCompressionTypes.None_: "None",
            GenericCompressionTypes.Uncompressed: "Uncompressed",
            GenericCompressionTypes.Zstd: "Zstd",
            GenericCompressionTypes.Zip: "Zip",
            GenericCompressionTypes.Bzip: "Bzip",
            GenericCompressionTypes.Match: "Match",
        }[self]


# Image
class ImageFormatTypes(Enum):
    None_ = 0x00
    Mask = 0x01
    Luminance = 0x02
    Depth = 0x03
    Rgb = 0x04
    Bgr = 0x05
    Rgba = 0x06
    Bgra = 0x07
    Hsv = 0x08
    Lab = 0x09
    Yuv422 = 0x0A
    Nv12 = 0x0B
    Yuv420 = 0x0C
    Yuv444 = 0x0D
    Match = 0xFF

    def as_u8(self) -> uint8: return uint8(self.value)

    @staticmethod
    def from_u8(value: uint8) -> ImageFormatTypes | None:
        try:
            return ImageFormatTypes(value)
        except ValueError:
            return None

    def name_str(self) -> str:
        return {
            ImageFormatTypes.None_: "None",
            ImageFormatTypes.Mask: "Mask",
            ImageFormatTypes.Luminance: "Luminance",
            ImageFormatTypes.Depth: "Depth",
            ImageFormatTypes.Rgb: "RGB",
            ImageFormatTypes.Bgr: "BGR",
            ImageFormatTypes.Rgba: "RGBA",
            ImageFormatTypes.Bgra: "BGRA",
            ImageFormatTypes.Hsv: "HSV",
            ImageFormatTypes.Lab: "LAB",
            ImageFormatTypes.Yuv422: "YUV422",
            ImageFormatTypes.Nv12: "NV12",
            ImageFormatTypes.Yuv420: "YUV420",
            ImageFormatTypes.Yuv444: "YUV444",
            ImageFormatTypes.Match: "Match",
        }[self]

    def num_channels(self) -> int | None:
        table = {
            ImageFormatTypes.Mask: 1,
            ImageFormatTypes.Luminance: 1,
            ImageFormatTypes.Depth: 1,
            ImageFormatTypes.Rgb: 3,
            ImageFormatTypes.Bgr: 3,
            ImageFormatTypes.Hsv: 3,
            ImageFormatTypes.Lab: 3,
            ImageFormatTypes.Yuv422: 3,
            ImageFormatTypes.Yuv420: 3,
            ImageFormatTypes.Yuv444: 3,
            ImageFormatTypes.Rgba: 4,
            ImageFormatTypes.Bgra: 4,
            ImageFormatTypes.Nv12: 3,
        }
        return table.get(self)


class ImageCompressionTypes(Enum):
    None_ = 0x00
    Uncompressed = 0x01
    Jpeg = 0x02
    Png = 0x03
    Tiff = 0x04
    H264 = 0x05
    H265 = 0x06
    Zdepth = 0x07
    Match = 0xFF

    def as_u8(self) -> uint8: return uint8(self.value)

    @staticmethod
    def from_u8(value: uint8) -> ImageCompressionTypes | None:
        try:
            return ImageCompressionTypes(value)
        except ValueError:
            return None

    def name_str(self) -> str:
        return {
            ImageCompressionTypes.None_: "None",
            ImageCompressionTypes.Uncompressed: "Uncompressed",
            ImageCompressionTypes.Jpeg: "JPEG",
            ImageCompressionTypes.Png: "PNG",
            ImageCompressionTypes.Tiff: "TIFF",
            ImageCompressionTypes.H264: "H264",
            ImageCompressionTypes.H265: "H265",
            ImageCompressionTypes.Zdepth: "ZDepth",
            ImageCompressionTypes.Match: "Match",
        }[self]


# Geometry
class GeometryFormatTypes(Enum):
    None_ = 0x00
    Point = 0x01
    Anchor = 0x02
    Sprite = 0x03
    SurfaceMesh = 0x04
    Spline = 0x05
    Nurbs = 0x06
    VoxelGrid = 0x07
    SparseVoxelGrid = 0x08
    Match = 0xFF

    def as_u8(self) -> uint8: return uint8(self.value)

    @staticmethod
    def from_u8(value: uint8) -> GeometryFormatTypes | None:
        try:
            return GeometryFormatTypes(value)
        except ValueError:
            return None

    def name_str(self) -> str:
        return {
            GeometryFormatTypes.None_: "None",
            GeometryFormatTypes.Point: "Point",
            GeometryFormatTypes.Anchor: "Anchor",
            GeometryFormatTypes.Sprite: "Sprite",
            GeometryFormatTypes.SurfaceMesh: "SurfaceMesh",
            GeometryFormatTypes.Spline: "Spline",
            GeometryFormatTypes.Nurbs: "Nurbs",
            GeometryFormatTypes.VoxelGrid: "VoxelGrid",
            GeometryFormatTypes.SparseVoxelGrid: "SparseVoxelGrid",
            GeometryFormatTypes.Match: "Match",
        }[self]


class GeometryCompressionTypes(Enum):
    None_ = 0x00
    Uncompressed = 0x01
    Draco = 0x02
    Match = 0xFF

    def as_u8(self) -> uint8: return uint8(self.value)

    @staticmethod
    def from_u8(value: uint8) -> GeometryCompressionTypes | None:
        try:
            return GeometryCompressionTypes(value)
        except ValueError:
            return None

    def name_str(self) -> str:
        return {
            GeometryCompressionTypes.None_: "None",
            GeometryCompressionTypes.Uncompressed: "Uncompressed",
            GeometryCompressionTypes.Draco: "Draco",
            GeometryCompressionTypes.Match: "Match",
        }[self]


class GeometryAttributes(Enum):
    None_ = 0x00
    Position = 0x01
    Normal = 0x02
    TextureCoordinate = 0x04
    Radius = 0x08
    Color = 0x10
    Face = 0x20
    Covariance = 0x40
    Id = 0x80
    Match = 0xFF

    def as_u8(self) -> uint8: return uint8(self.value)

    @staticmethod
    def from_u8(value: uint8) -> GeometryAttributes | None:
        try:
            return GeometryAttributes(value)
        except ValueError:
            return None

    def name_str(self) -> str:
        return {
            GeometryAttributes.None_: "None",
            GeometryAttributes.Id: "Id",
            GeometryAttributes.Position: "Position",
            GeometryAttributes.Normal: "Normal",
            GeometryAttributes.TextureCoordinate: "TextureCoordinate",
            GeometryAttributes.Radius: "Radius",
            GeometryAttributes.Color: "Color",
            GeometryAttributes.Face: "Face",
            GeometryAttributes.Covariance: "Covariance",
            GeometryAttributes.Match: "Match",
        }[self]


# Transform
class TransformFormatTypes(Enum):
    None_ = 0x00
    Translation = 0x01
    Rotation = 0x02
    Scaling = 0x03
    RigidTransform = 0x04
    SimilarityTransform = 0x05
    AffineTransform = 0x06
    ProjectiveTransform = 0x07
    Acceleration = 0x08
    Match = 0xFF

    def as_u8(self) -> uint8: return uint8(self.value)

    @staticmethod
    def from_u8(value: uint8) -> TransformFormatTypes | None:
        try:
            return TransformFormatTypes(value)
        except ValueError:
            return None

    def name_str(self) -> str:
        return {
            TransformFormatTypes.None_: "None",
            TransformFormatTypes.Translation: "Translation",
            TransformFormatTypes.Rotation: "Rotation",
            TransformFormatTypes.Scaling: "Scaling",
            TransformFormatTypes.RigidTransform: "RigidTransform",
            TransformFormatTypes.SimilarityTransform: "SimilarityTransform",
            TransformFormatTypes.AffineTransform: "AffineTransform",
            TransformFormatTypes.ProjectiveTransform: "ProjectiveTransform",
            TransformFormatTypes.Acceleration: "Acceleration",
            TransformFormatTypes.Match: "Match",
        }[self]


class TransformCompressionTypes(Enum):
    None_ = 0x00
    Match = 0xFF

    def as_u8(self) -> uint8: return uint8(self.value)

    @staticmethod
    def from_u8(value: uint8) -> TransformCompressionTypes | None:
        try:
            return TransformCompressionTypes(value)
        except ValueError:
            return None

    def name_str(self) -> str:
        return {
            TransformCompressionTypes.None_: "None",
            TransformCompressionTypes.Match: "Match",
        }[self]


class TransformDetailTypes(Enum):
    None_ = 0x00
    KinectBodyTracking = 0x01
    Match = 0xFF

    def as_u8(self) -> uint8: return uint8(self.value)

    @staticmethod
    def from_u8(value: uint8) -> TransformDetailTypes | None:
        try:
            return TransformDetailTypes(value)
        except ValueError:
            return None

    def name_str(self) -> str:
        return {
            TransformDetailTypes.None_: "None",
            TransformDetailTypes.KinectBodyTracking: "KinectBodyTracking",
            TransformDetailTypes.Match: "Match",
        }[self]


class EmptyCustomType(Enum):
    None_ = 0x00
    Match = 0xFF

    def as_u8(self) -> uint8: return uint8(self.value)

    @staticmethod
    def from_u8(value: uint8) -> EmptyCustomType | None:
        try:
            return EmptyCustomType(value)
        except ValueError:
            return None

    def name_str(self) -> str:
        return {
            EmptyCustomType.None_: "None",
            EmptyCustomType.Match: "Match",
        }[self]


class EmptyMaskType(Enum):
    None_ = 0x00
    Match = 0xFF

    def as_u8(self) -> uint8: return uint8(self.value)

    @staticmethod
    def from_u8(value: uint8) -> EmptyMaskType | None:
        try:
            return EmptyMaskType(value)
        except ValueError:
            return None

    def name_str(self) -> str:
        return {
            EmptyMaskType.None_: "None",
            EmptyMaskType.Match: "Match",
        }[self]
