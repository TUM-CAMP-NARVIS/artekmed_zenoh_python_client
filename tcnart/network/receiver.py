from __future__ import annotations
import threading
import time
from typing import Any, Dict, List, Optional
import logging

import zenoh  # type: ignore

from .common import _get_attachment, _extract_payload, _declare_subscriber
from ..serialization.cdr_serialization import decode_raw_message
from ..serialization.error import MessageError
from ..schema.messages.common import InvalidMessage
from ..core.frames import Frame, FrameAnnotation
from ..core.dataflow import StreamConfig

log = logging.getLogger(__name__)


# Function to receive messages from Zenoh - synchronous distribution to workers

def receive_zenoh_messages(
    session: Any,
    topic: str,
    source: str,
    stream_index: int,
    worker_index: int,
    semantic_type: int,
    sender: Any,  # queue-like with put(), callable, or list
    annotations: Dict[str, FrameAnnotation],
    shutdown_event: Optional[Any] = None,
    wait_poll_ms: int = 100,
) -> None:
    if zenoh is None:
        raise MessageError(MessageError.NETWORK_ERROR, "zenoh is not available")

    rx: List[Any] = []
    sub = _declare_subscriber(session, topic, rx)
    default_type = "tcnart_msgs::msg::VideoStreamMessage"  # best-effort default

    log.info(f"Starting receiver for {source} @ {topic}")
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
                    msg = InvalidMessage()

                if hasattr(msg, "get_timestamp"):
                    ts = int(msg.get_timestamp())
                else:
                    # Cannot determine timestamp; skip
                    ts = 0

                if ts != 0:
                    frame = Frame.create(ts, int(semantic_type), int(stream_index), msg)
                    for k, v in annotations.items():
                        frame.add_annotation(k, v)

                    # Dispatch to sender
                    if hasattr(sender, "put") and callable(getattr(sender, "put")):
                        sender.put(frame)
                    elif callable(sender):
                        sender(frame)
                    elif isinstance(sender, list):
                        sender.append(frame)
                    else:
                        # No valid sink; drop
                        log.warning(f"No valid sink for {source}")
                        pass
            else:
                time.sleep(wait_poll_ms / 1000.0)
    finally:
        try:
            sub.undeclare()
        except Exception as e:
            log.exception(e)

    # Send final invalid message to own worker index sink
    if stream_index == worker_index:
        frame = Frame.create(0, 0, int(worker_index), InvalidMessage())
        if hasattr(sender, "put") and callable(getattr(sender, "put")):
            sender.put(frame)
        elif callable(sender):
            sender(frame)
        elif isinstance(sender, list):
            sender.append(frame)


# Helper orchestration functions (synchronous variants)

def resolve_stream_descriptors(
    topic_prefix: str,
    shutdown_event: Optional[Any],
    channel_calibrations: Dict[str, Any],
    channel_poses: Dict[str, Any],
    channels_config: List[tuple[str, str, str]],
    session: Any,
) -> Dict[str, StreamConfig]:
    from .discovery import get_or_waitfor_descriptor

    channels: Dict[str, StreamConfig] = {}
    for i, (sensor, name, topic) in enumerate(channels_config):
        log.info(f"Found sensor: {name} @ {topic}")
        calibration = channel_calibrations.get(sensor)
        pose = channel_poses.get(sensor)
        cfg = get_or_waitfor_descriptor(
            session=session,
            sensor=sensor,
            stream_index=i,
            name=name,
            topic=f"{topic_prefix}/{topic}",
            calibration=calibration,
            pose=pose,
            shutdown_event=shutdown_event,
        )
        channels[cfg.stream_name] = cfg
    return channels


def start_all_receivers(
    num_workers: int,
    shutdown_event: Optional[Any],
    worker_senders: List[Any],
    session: Any,
    channels: Dict[str, StreamConfig],
) -> List[threading.Thread]:
    threads: List[threading.Thread] = []

    for key, config in channels.items():
        descriptor = getattr(config, "descriptor", None)
        if descriptor is None:
            continue
        topic = getattr(descriptor, "stream_topic", None)
        if callable(topic):
            topic = descriptor.stream_topic  # dataclass attribute
        if not isinstance(topic, str):
            # Attempt attribute access as field
            try:
                topic = descriptor.stream_topic  # type: ignore[attr-defined]
            except Exception as e:
                log.exception(e)
                continue

        # Semantic type from buffer info
        try:
            buffer_info = descriptor.buffer_info  # dataclass field
            semantic_type = int(getattr(buffer_info, "semantic_type", 0))
        except Exception as e:
            log.exception(e)
            semantic_type = 0

        stream_id = int(config.stream_id)
        worker_id = stream_id % max(1, num_workers)
        sender = worker_senders[worker_id]
        annotations = dict(config.annotations)

        t = threading.Thread(
            target=receive_zenoh_messages,
            kwargs=dict(
                session=session,
                topic=topic,
                source=key,
                stream_index=stream_id,
                worker_index=worker_id,
                semantic_type=semantic_type,
                sender=sender,
                annotations=annotations,
                shutdown_event=shutdown_event,
            ),
            daemon=True,
        )
        t.start()
        threads.append(t)

    return threads
