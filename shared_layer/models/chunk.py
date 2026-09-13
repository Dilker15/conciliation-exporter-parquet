from dataclasses import dataclass
from datetime import datetime
from typing import Literal


ChunkStatus = Literal["PROCESSING", "COMPLETED", "FAILED"]


@dataclass
class Chunk:
    file_id: str
    chunk_id: str
    bucket_name: str
    bucket_key: str
    created_at: datetime
    status: ChunkStatus = "PROCESSING"
    finished_at: datetime | None = None
