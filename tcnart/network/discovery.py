from __future__ import annotations
import time
from typing import Optional, List, Dict, Any, Tuple
import logging

import zenoh  # type: ignore

from .common import _get_attachment, _extract_payload, _declare_subscriber, _do_get
from ..serialization.cdr_serialization import decode_raw_message, encode_raw_message
from ..serialization.error import MessageError
from ..schema.messages.rpc import NullRequest
from ..schema.messages.service_controller import DeviceContextReply
from ..schema.messages.stream import StreamDescriptorMessage
from ..schema.types.primitives import CameraModel
from ..schema.types.transform import RigidTransform
from ..core.dataflow import StreamConfig
from ..core.frames import FrameAnnotation


log = logging.getLogger(__name__)



# Public API

def get_or_waitfor_descriptor(
    session: Any,
    sensor: str,
    stream_index: int,
    name: str,
    topic: str,
    calibration: Optional[CameraModel] = None,
    pose: Optional[RigidTransform] = None,
    shutdown_event: Optional[Any] = None,
    wait_poll_ms: int = 100,
) -> StreamConfig:
    # First attempt: GET request
    default_type = "tcnart_msgs::msg::StreamDescriptorMessage"
    try:
        samples = _do_get(session, topic, payload=b"")
    except Exception as e:
        log.exception(e)
        samples = []
    stream_config: Optional[StreamConfig] = None
    for sample in samples:
        type_name = _get_attachment(sample, default_type)
        payload = _extract_payload(sample)
        try:
            msg = decode_raw_message(type_name, payload)
        except MessageError as e:
            log.exception(e)
            continue
        if isinstance(msg, StreamDescriptorMessage):
            cfg = StreamConfig.new(stream_index, name, topic)
            cfg.sensor_name = sensor
            # annotations
            try:
                cfg.add_annotation("BufferInfo", FrameAnnotation.buffer_info(msg.buffer_info))  # type: ignore[attr-defined]
            except Exception as e:
                log.exception(e)
                pass
            if calibration is not None:
                cfg.add_annotation("CameraModel", FrameAnnotation.camera_model(calibration))
            if pose is not None:
                cfg.add_annotation("SensorPose", FrameAnnotation.sensor_pose(pose))
            cfg.descriptor = msg
            stream_config = cfg
            break
    if stream_config is not None:
        return stream_config

    # Fallback: subscribe and wait until message arrives or shutdown
    rx: List[Any] = []
    sub = _declare_subscriber(session, topic, rx)
    try:
        while True:
            if shutdown_event is not None and getattr(shutdown_event, "is_set", lambda: False)():
                break
            if rx:
                sample = rx.pop(0)
                type_name = _get_attachment(sample, default_type)
                payload = _extract_payload(sample)
                try:
                    msg = decode_raw_message(type_name, payload)
                except MessageError as e:
                    log.exception(e)
                    msg = None
                if isinstance(msg, StreamDescriptorMessage):
                    cfg = StreamConfig.new(stream_index, name, topic)
                    cfg.sensor_name = sensor
                    cfg.descriptor = msg
                    return cfg
            time.sleep(wait_poll_ms / 1000.0)
    finally:
        try:
            sub.undeclare()
        except Exception as e:
            log.exception(e)

    raise MessageError(MessageError.NETWORK_ERROR, "Failed to discover stream config")


def find_camera_sensors(session: Any, topic: str) -> List[DeviceContextReply]:
    # Send a null request if possible; otherwise, mimic by sending empty payload
    payload: Optional[bytes]
    try:
        payload = encode_raw_message(NullRequest(), type_name=None)  # may raise
    except Exception as e:
        log.exception(e)
        payload = b""

    default_type = "pcpd_msgs::rpc::DeviceContextReply"
    try:
        samples = _do_get(session, topic, payload=payload)
    except Exception as e:
        raise MessageError(MessageError.NETWORK_ERROR, str(e))

    sensors: List[DeviceContextReply] = []
    for sample in samples:
        type_name = _get_attachment(sample, default_type)
        bytes_payload = _extract_payload(sample)
        try:
            msg = decode_raw_message(type_name, bytes_payload)
        except MessageError as e:
            log.exception(e)
            continue
        if isinstance(msg, DeviceContextReply):
            sensors.append(msg)
        else:
            log.warning(f"Unknown message type: {type_name}")
    return sensors

def build_channel_configs(
    sensors: List[DeviceContextReply],
) -> Tuple[List[Tuple[str, str, str]], Dict[str, CameraModel], Dict[str, RigidTransform]]:
    channels_config: List[Tuple[str, str, str]] = []
    channel_calibrations: Dict[str, CameraModel] = {}
    channel_poses: Dict[str, RigidTransform] = {}

    for sensor in list(sensors):
        name = sensor.name
        sensor_info = sensor.value  # CameraSensorMessage

        # Streams for color
        if sensor_info.color_enabled:
            stream_color = f"{name}_color"
            topic_color = f"{name}/cfg/dsc/color_image_bitstream"
            channels_config.append((name, stream_color, topic_color))
            # Use the color camera intrinsics for the color stream
            channel_calibrations[name] = sensor_info.color_parameters
            # Pose from color to depth; for a single color stream this is a useful extrinsic
            channel_poses[name] = sensor_info.color2depth_transform

        # Streams for depth
        if sensor_info.depth_enabled:
            stream_depth = f"{name}_depth"
            topic_depth = f"{name}/cfg/dsc/depth_image_bitstream"
            channels_config.append((name, stream_depth, topic_depth))
            # Use the depth camera intrinsics for the depth stream
            channel_calibrations[name] = sensor_info.depth_parameters
            # Sensor/world pose as provided
            channel_poses[name] = sensor_info.camera_pose

        # TODO: IR stream handling if needed

    return channels_config, channel_calibrations, channel_poses