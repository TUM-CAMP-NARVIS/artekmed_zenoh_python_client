from dataclasses import dataclass, field
from pycdr2 import IdlStruct, IdlEnum, IdlUnion
from pycdr2.types import sequence, float64, default, case

from ..types.math import Vector3
from ..types.transform import RigidTransform
from .spatial_relations import CoordinateSystem

from ...serialization.cdr_serialization import register_type


class SISScope(IdlEnum, typename="SISScope"):
    SIS_SCOPE_LOCAL = 0
    SIS_SCOPE_GLOBAL = 1


class SISTransformationType(IdlEnum, typename="SISTransformationType"):
    SIS_TRANSFORM_POSE6D = 0
    SIS_TRANSFORM_TRANSLATION3D = 1

class SISTransformation(IdlUnion, typename="SISTransformation", discriminator=SISTransformationType):
    value_6d: case[SISTransformationType.SIS_TRANSFORM_POSE6D, RigidTransform]
    value_3d: case[SISTransformationType.SIS_TRANSFORM_TRANSLATION3D, Vector3]

@dataclass
class SISComponentRef(IdlStruct, typename="SISComponentRef"):
    name: str = ""


@dataclass
class SISRelationRef(IdlStruct, typename="SISRelationRef"):
    from_: SISComponentRef = field(default_factory=SISComponentRef, metadata={"idl_name": "from"})
    to: SISComponentRef = field(default_factory=SISComponentRef)


@dataclass
class SISComponentMessage(IdlStruct, typename="SISComponentMessage"):
    node: SISComponentRef = field(default_factory=SISComponentRef)
    coord: CoordinateSystem = field(default_factory=CoordinateSystem)
    active: bool = False
    scope: SISScope = SISScope.SIS_SCOPE_LOCAL
    tracker_stream_descriptor_topic: str = ""


@dataclass
class SISRelationMessage(IdlStruct, typename="SISRelationMessage"):
    edge: SISRelationRef = field(default_factory=SISRelationRef)
    transform: SISTransformation = field(default_factory=SISTransformation)
    weight: float64 = 0.0
    tracker_stream_descriptor_topic: str = ""


@dataclass
class SISJoinMessage(IdlStruct, typename="SISJoinMessage"):
    origin: SISComponentRef = field(default_factory=SISComponentRef)
    components: sequence[SISComponentMessage] = field(default_factory=list)
    relations: sequence[SISRelationMessage] = field(default_factory=list)


@dataclass
class SISTopicTranslationStartRequest(IdlStruct, typename="SISTopicTranslationStartRequest"):
    src_topic: str = ""
    dst_topic: str = ""
    src_client: str = ""
    dst_client: str = ""
    src_node: SISComponentRef = field(default_factory=SISComponentRef)
    dst_node: SISComponentRef = field(default_factory=SISComponentRef)


@dataclass
class SISTopicTranslationStopRequest(IdlStruct, typename="SISTopicTranslationStopRequest"):
    src_topic: str = ""
    dst_topic: str = ""


class SISTopicTranslationStatusReply(IdlEnum, typename="SISTopicTranslationStatusReply"):
    SIS_TTSTATUS_ACTIVE = 0
    SIS_TTSTATUS_INACTIVE = 1
    SIS_TTSTATUS_UNAVAILABLE = 2


# Register schema type name mapping
register_type("tcnart_msgs::msg::SISJoinMessage", SISJoinMessage)
register_type("tcnart_msgs::msg::SISTopicTranslationStartRequest", SISTopicTranslationStartRequest)
register_type("tcnart_msgs::msg::SISTopicTranslationStopRequest", SISTopicTranslationStopRequest)
register_type("tcnart_msgs::msg::SISTopicTranslationStatusReply", SISTopicTranslationStatusReply)
