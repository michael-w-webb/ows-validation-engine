"""
Temporary file storage service.

This module manages temporary persisted files for
multi-request application workflows.

Responsibilities
----------------
- temporary file creation
- file retrieval
- access timestamp tracking
- expiration cleanup
- temporary file deletion

Files are stored in the OS temp directory under an
application-specific subdirectory.
"""

from __future__ import annotations

import json
import tempfile
import uuid

from datetime import datetime, timedelta, UTC
from pathlib import Path

import logging 

logger = logging.getLogger(__name__)

# ==================================================
# Configuration
# ==================================================

TEMP_DIR = Path(tempfile.gettempdir()) / "ows_temp_storage"

TEMP_DIR.mkdir(exist_ok=True)

EXPIRATION_MINUTES = 30


# ==================================================
# Internal Helpers
# ==================================================

def _resource_path(
    resource_id: str,
    suffix: str
) -> Path:
    """
    Construct filesystem path for a temporary resource.
    """

    return TEMP_DIR / f"{resource_id}{suffix}"


def _metadata_path(
    resource_id: str
) -> Path:
    """
    Construct metadata path for a temporary resource.
    """

    return TEMP_DIR / f"{resource_id}.json"


def _utc_now_iso() -> str:
    """
    Generate current UTC timestamp in ISO format.
    """

    return datetime.now(UTC).isoformat()


# ==================================================
# Public API
# ==================================================

def create_temp_file(
    contents: bytes,
    suffix: str = ""
) -> str:
    """
    Create a temporary persisted file.

    Parameters
    ----------
    contents : bytes
        Raw file contents.

    suffix : str, optional
        File suffix including extension.

        Example:
            ".xlsx"

    Returns
    -------
    str
        Generated resource ID.
    """

    logger.info("Creating temporary file with suffix %s", suffix)

    resource_id = str(uuid.uuid4())

    resource_path = _resource_path(
        resource_id,
        suffix
    )

    metadata_path = _metadata_path(resource_id)

    # ----------------------------------------------
    # Save resource
    # ----------------------------------------------

    with open(resource_path, "wb") as f:

        f.write(contents)

    # ----------------------------------------------
    # Save metadata
    # ----------------------------------------------

    metadata = {
        "resource_id": resource_id,
        "suffix": suffix,
        "created_at": _utc_now_iso(),
        "last_accessed": _utc_now_iso()
    }

    with open(metadata_path, "w") as f:

        json.dump(metadata, f)

    logger.info("Temporary file created with resource_id=%s", resource_id)

    return resource_id


def load_temp_file_path(
    resource_id: str
) -> Path:
    """
    Retrieve temporary file path and refresh access time.

    Parameters
    ----------
    resource_id : str
        Temporary resource identifier.

    Returns
    -------
    Path
        Filesystem path to temporary resource.

    Raises
    ------
    FileNotFoundError
        If resource does not exist.
    """

    logger.info("Loading temporary file path for resource_id=%s", resource_id)

    metadata = get_resource_metadata(resource_id)

    suffix = metadata["suffix"]

    resource_path = _resource_path(
        resource_id,
        suffix
    )

    if not resource_path.exists():

        logger.warning("Resource %s does not exist.", resource_id)

        raise FileNotFoundError(
            f"Resource {resource_id} does not exist."
        )

    touch_temp_file(resource_id)

    logger.info("Loaded temporary file path for resource_id=%s: %s", resource_id, resource_path)

    return resource_path


def get_resource_metadata(
    resource_id: str
) -> dict:
    """
    Load metadata for temporary resource.

    Parameters
    ----------
    resource_id : str
        Temporary resource identifier.

    Returns
    -------
    dict
        Resource metadata dictionary.

    Raises
    ------
    FileNotFoundError
        If metadata does not exist.
    """

    logger.info("Retrieving metadata for resource_id=%s", resource_id)

    metadata_path = _metadata_path(resource_id)

    if not metadata_path.exists():

        raise FileNotFoundError(
            f"Metadata for resource {resource_id} not found."
        )

    with open(metadata_path, "r") as f:

        metadata = json.load(f)

    return metadata


def touch_temp_file(
    resource_id: str
) -> None:
    """
    Refresh temporary file access timestamp.
    """

    metadata = get_resource_metadata(resource_id)

    metadata["last_accessed"] = _utc_now_iso()

    metadata_path = _metadata_path(resource_id)

    with open(metadata_path, "w") as f:

        json.dump(metadata, f)


def delete_temp_file(
    resource_id: str
) -> None:
    """
    Delete temporary resource and metadata.
    """

    try:

        logger.info("Deleting temporary file for resource_id=%s", resource_id)

        metadata = get_resource_metadata(resource_id)

        suffix = metadata["suffix"]

        resource_path = _resource_path(
            resource_id,
            suffix
        )

        metadata_path = _metadata_path(resource_id)

        if resource_path.exists():

            resource_path.unlink()

        if metadata_path.exists():

            metadata_path.unlink()

    except FileNotFoundError:

        logger.error("Unable to find resource %s. May already have been deleted.", resource_id)

        return


def cleanup_expired_files() -> None:
    """
    Delete expired temporary resources.
    """

    now = datetime.now(UTC)

    logger.info("Starting cleanup of expired temporary files at %s", now.isoformat())

    for metadata_path in TEMP_DIR.glob("*.json"):

        resource_id = "UNKNOWN"

        try:

            with open(metadata_path, "r") as f:

                metadata = json.load(f)

            resource_id = metadata["resource_id"]

            last_accessed = datetime.fromisoformat(
                metadata["last_accessed"]
            )

            if last_accessed.tzinfo is None:

                last_accessed = last_accessed.replace(
                    tzinfo=UTC
                )

            age = now - last_accessed

            if age > timedelta(minutes=EXPIRATION_MINUTES):

                delete_temp_file(resource_id)

        except Exception:

            # Fail-safe cleanup behavior:
            # ignore malformed metadata
            logger.exception("Error occurred while cleaning up expired file for resource_id=%s", resource_id)
            continue

def update_resource_metadata(
    resource_id: str,
    updates: dict
) -> None:
    """
    Update temporary resource metadata.
    """

    logger.info("Updating metadata for resource_id=%s with updates: %s", resource_id, updates)

    metadata = get_resource_metadata(resource_id)

    metadata.update(updates)

    metadata_path = _metadata_path(resource_id)

    with open(metadata_path, "w") as f:

        json.dump(metadata, f)

    logger.info("Updated metadata for resource_id=%s", resource_id)

def get_metadata_value(
    resource_id: str,
    key: str,
    default=None
):
    """
    Retrieve metadata value for resource.
    """

    logger.info("Retrieving metadata value for resource_id=%s, key=%s", resource_id, key)

    metadata = get_resource_metadata(
        resource_id
    )

    return metadata.get(
        key,
        default
    )
