from __future__ import annotations  # Future-proof typing of annotations

import json  # JSON serialisation
from datetime import datetime, timezone  # Time utilities for UTC timestamps
from pathlib import Path  # Filesystem path handling
from typing import Any, Dict  # General-purpose types


def write_report(payload: Dict[str, Any], output_path: Path) -> Path:

    output_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    with output_path.open("w", encoding="utf-8") as handle:  # Open for writing text
        json.dump(payload, handle, indent=2)  # Write pretty-printed JSON
    return output_path  # Return the path for convenience


def iso_timestamp() -> str:
    """Return a UTC timestamp suitable for JSON serialisation."""

    return datetime.now(timezone.utc).isoformat()  # e.g., 2025-10-20T18:09:39+00:00


__all__ = ["write_report", "iso_timestamp"]  # Public API
