from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal


@dataclass
class ChunkCounterData:
    file_id: str
    total_chunks: int
    processed_chunk_indexes: list[int] = field(default_factory=list)
    status: Literal["PROCESSING", "COMPLETED"] = "PROCESSING"
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )