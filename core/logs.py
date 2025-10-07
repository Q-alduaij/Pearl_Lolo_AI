import json
import time
import uuid
import sys
from typing import Any, Dict


def _ts_ms() -> int:
    return int(time.time() * 1000)


def log(event: str, **fields: Any) -> None:
    rec: Dict[str, Any] = {"ts": _ts_ms(), "event": event, **fields}
    sys.stdout.write(json.dumps(rec, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def new_request_id() -> str:
    return str(uuid.uuid4())
