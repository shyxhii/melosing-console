"""storage.py - save and load records as JSON (SUBSYSTEM 2)."""

import json


def save_data(filename, data):
    """Write a list of records to a JSON file (replaces the old file)."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def load_data(filename):
    """Load a list of records. A missing file gives an empty list.

    Raises ValueError if the file is corrupted.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            records = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        raise ValueError(f"{filename} is corrupted")
    if not isinstance(records, list):
        raise ValueError(f"{filename} has an invalid format")
    return records
