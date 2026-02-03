from __future__ import annotations
from typing import Any, List
import zenoh
import logging
from typing import Optional


def _get_topic(sample: Any) -> str:
    return str(getattr(sample, "key_expr", ""))

def _get_attachment(sample: Any, default: str) -> str:
    # Try different attribute layouts depending on zenoh-python version
    att = getattr(sample, "attachment")
    try:
        # some versions expose bytes/bytearray
        if att is None:
            return default
        return att.to_string()
    except Exception as e:
        log.exception(e)
    return default


def _extract_payload(sample: Any) -> bytes:
    try:
        pay = getattr(sample, "payload")
        if isinstance(pay, (bytes, bytearray)):
            return bytes(pay)
        elif isinstance(pay, zenoh.ZBytes):
            return pay.to_bytes()
    except Exception as e:
        log.exception(e)
        pass
    return b""


def _declare_subscriber(session: Any, key_expr: str, queue: List[Any]) -> Any:
    def _cb(sample: Any) -> None:
        queue.append(sample)
    return session.declare_subscriber(key_expr, _cb)


def _do_get(session: Any, key_expr: str, payload: Optional[bytes] = None) -> List[Any]:
    out = []
    for reply in session.get(key_expr, payload=payload, encoding=zenoh.Encoding.APPLICATION_CDR):
        out.append(reply.ok)
    return out
