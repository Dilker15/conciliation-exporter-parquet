import pyarrow as pa
import pyarrow.parquet as pq


schema = pa.schema([
    ("settlement_id", pa.string()),
    ("transaction_id",pa.string()),
    ("file_id", pa.string()),
    ("amount", pa.float64()),
    ("currency", pa.string()),
    ("provider", pa.string()),
    ("status", pa.string()),
    ("created_at", pa.string()),
])


class ParquetWriterService:

    def __init__(self):
        self._writer = None
        self._file_path = None

    def start(self, file_path: str):
        self._writer = None
        self._file_path = file_path

    def write_batch(self, items: list[dict]):

        table = pa.Table.from_pylist(
            items,
            schema=schema
        )

        if self._writer is None:
            self._writer = pq.ParquetWriter(
                self._file_path,
                schema=schema
            )

        self._writer.write_table(table)

    def close(self):

        if self._writer:
            self._writer.close()
            self._writer = None