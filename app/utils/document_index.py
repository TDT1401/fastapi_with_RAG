import os
import secrets
from typing import Literal

PERSISTENT_DIRECTORY = os.path.join("db")
ReasoningType = Literal["wp", "pdf", "md"]
REASONING_TYPES: tuple[ReasoningType, ...] = ("wp", "pdf", "md")


def generate_website_id(website_name: str) -> str:
    """Return an unused website index ID with a five-digit random suffix."""
    while True:
        website_id = f"{website_name}_{secrets.randbelow(90000) + 10000}"
        db_path = os.path.join(
            PERSISTENT_DIRECTORY, "chroma_db_wp_ollama", website_id
        )
        if not os.path.exists(db_path):
            return website_id


def list_document_choices() -> list[tuple[str, ReasoningType]]:
    """List valid ChromaDB index IDs and their source types."""
    document_choices: list[tuple[str, ReasoningType]] = []
    for reasoning_type in REASONING_TYPES:
        store_directory = os.path.join(
            PERSISTENT_DIRECTORY, f"chroma_db_{reasoning_type}_ollama"
        )
        if not os.path.isdir(store_directory):
            continue

        for entry in os.scandir(store_directory):
            if entry.is_dir() and os.path.isfile(
                os.path.join(entry.path, "chroma.sqlite3")
            ):
                document_choices.append((entry.name, reasoning_type))

    return sorted(document_choices, key=lambda document: (document[1], document[0]))
