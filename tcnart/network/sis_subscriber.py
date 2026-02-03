from __future__ import annotations
import threading
import time
from typing import Any, Dict, List, Optional
import logging

import zenoh  # type: ignore

from .common import _get_attachment, _extract_payload, _declare_subscriber
from ..serialization.cdr_serialization import decode_raw_message
from ..serialization.error import MessageError
from ..schema.messages.srg_engine import SISJoinMessage
from ..schema.messages.common import InvalidMessage
from ..core.frames import Frame, FrameAnnotation
from ..core.dataflow import StreamConfig

log = logging.getLogger(__name__)



def sis_join_subscriber(
    session: Any,
    topic: str,
    sender: Any,  # queue-like with put(), callable, or list
    shutdown_event: Optional[Any] = None,
    wait_poll_ms: int = 100,
) -> None:

    rx: List[Any] = []
    sub = _declare_subscriber(session, topic, rx)
    default_type = "tcnart_msgs::msg::SISJoinMessage"  # best-effort default

    log.info(f"Starting receiver for {topic}")
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

                # Dispatch to sender
                if hasattr(sender, "put") and callable(getattr(sender, "put")):
                    sender.put(msg)
                elif callable(sender):
                    sender(msg)
                elif isinstance(sender, list):
                    sender.append(msg)
                else:
                    # No valid sink; drop
                    log.warning(f"No valid sink for {topic}")
                    pass
            else:
                time.sleep(wait_poll_ms / 1000.0)
    finally:
        try:
            sub.undeclare()
        except Exception as e:
            log.exception(e)

    # Send final invalid message to own worker index sink
    if hasattr(sender, "put") and callable(getattr(sender, "put")):
        sender.put(InvalidMessage())
    elif callable(sender):
        sender(InvalidMessage())
    elif isinstance(sender, list):
        sender.append(InvalidMessage())


def start_sis_join_subscriber(
    shutdown_event: Optional[Any],
    sender: Any,
    session: Any,
    topic: str,
) -> threading.Thread:

    t = threading.Thread(
        target=sis_join_subscriber,
        kwargs=dict(
            session=session,
            topic=topic,
            sender=sender,
            shutdown_event=shutdown_event,
        ),
        daemon=True,
    )
    t.start()
    return t
