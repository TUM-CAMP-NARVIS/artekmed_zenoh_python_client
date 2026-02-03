from dataclasses import dataclass, field
from pycdr2 import IdlStruct, IdlEnum
from pycdr2.types import int8, uint32, sequence

from ..types.common import UUID


class SRNodeType(IdlEnum, typename="SRNodeType"):
    SRG_NODE_NONE = 0
    SRG_NODE_GENERIC = 1
    SRG_NODE_SENSOR = 2
    SRG_NODE_DISPLAY = 3
    SRG_NODE_TRACKABLE = 4
    SRG_NODE_CONTENT = 5


class SREdgeTemporalType(IdlEnum, typename="SREdgeTemporalType"):
    SRG_EDGE_TEMPORAL_NONE = 0
    SRG_EDGE_TEMPORAL_STATIC = 1
    SRG_EDGE_TEMPORAL_STATIC_CALIBRATED = 2
    SRG_EDGE_TEMPORAL_DYNAMIC = 3
    SRG_EDGE_TEMPORAL_DYNAMIC_INFERRED = 4


class CoordinateAxis(IdlEnum, typename="CoordinateAxis"):
    X = 0
    XNegative = 1
    Y = 2
    YNegative = 3
    Z = 4
    ZNegative = 5


@dataclass
class CoordinateSystem(IdlStruct, typename="CoordinateSystem"):
    forward: CoordinateAxis = CoordinateAxis.X
    right: CoordinateAxis = CoordinateAxis.Y
    up: CoordinateAxis = CoordinateAxis.Z
    dimensions: int8 = 3


@dataclass
class SRNode(IdlStruct, typename="SRNode"):
    node_type: SRNodeType = SRNodeType.SRG_NODE_NONE
    node_uuid: UUID = field(default_factory=UUID)
    node_id: uint32 = 0
    node_name: str = ""
    custom_data: str = ""


@dataclass
class SREdge(IdlStruct, typename="SREdge"):
    edge_name: str = ""
    node_source_id: uint32 = 0
    node_destination_id: uint32 = 0
    temporal_type: SREdgeTemporalType = SREdgeTemporalType.SRG_EDGE_TEMPORAL_NONE
    data_type: str = ""
    uri: str = ""


@dataclass
class SRGraph(IdlStruct, typename="SRGraph"):
    graph_name: str = ""
    nodes: sequence[SRNode] = field(default_factory=list)
    edges: sequence[SREdge] = field(default_factory=list)

