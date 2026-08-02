"""File system and I/O utility operations."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Union

from .logger import get_logger

logger = get_logger("file_utils")


def get_project_root() -> Path:
    """Get absolute path to repository root directory.

    Returns:
        Path object pointing to repository root.
    """
    # Go 2 levels up from scripts/utils/file_utils.py
    return Path(__file__).resolve().parent.parent.parent


def ensure_dir(dir_path: Union[str, Path]) -> Path:
    """Ensure directory path exists, creating parents if necessary.

    Args:
        dir_path: Path string or Path object to verify/create.

    Returns:
        Path object for created directory.
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(file_path: Union[str, Path], fallback: Any = None) -> Any:
    """Read and parse JSON file safely with fallback on failure.

    Args:
        file_path: Absolute or relative path to target JSON file.
        fallback: Default object returned if file is missing or invalid.

    Returns:
        Parsed JSON content or fallback value.
    """
    path = Path(file_path)
    if not path.exists():
        logger.warning(f"File not found: {path}, using fallback.")
        return fallback

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as err:
        logger.error(f"Failed to parse JSON from {path}: {err}")
        return fallback


def write_json(file_path: Union[str, Path], data: Any, indent: int = 2) -> bool:
    """Serialize and write python structure to JSON file.

    Args:
        file_path: Output target file path.
        data: Data structure to serialize.
        indent: Indentation spacing level.

    Returns:
        True if write succeeded, False otherwise.
    """
    path = Path(file_path)
    ensure_dir(path.parent)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        logger.info(f"Saved JSON data to {path}")
        return True
    except Exception as err:
        logger.error(f"Failed writing JSON to {path}: {err}")
        return False


def read_text(file_path: Union[str, Path], fallback: str = "") -> str:
    """Read plain text content from file safely.

    Args:
        file_path: Path to target text file.
        fallback: Default string to return if missing.

    Returns:
        Text file contents string.
    """
    path = Path(file_path)
    if not path.exists():
        return fallback
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as err:
        logger.error(f"Error reading {path}: {err}")
        return fallback


def write_text(file_path: Union[str, Path], content: str) -> bool:
    """Write text content to target file safely.

    Args:
        file_path: Output target path.
        content: String content to write.

    Returns:
        True if written successfully.
    """
    path = Path(file_path)
    ensure_dir(path.parent)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Wrote file: {path}")
        return True
    except Exception as err:
        logger.error(f"Failed writing file {path}: {err}")
        return False
