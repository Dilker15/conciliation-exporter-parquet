import time
from pathlib import Path                                                        
from services.parquet_write_service import ParquetWriterService
from services.s3_service import S3Service
from services.settlement_service import SettlementService
from shared_layer.services.observability import get_logger
import os

logger = get_logger()

BUCKET_NAME = os.environ["BUCKET_NAME"]

class ExporterService:


    def __init__(self,s3_service:S3Service,parquet_service:ParquetWriterService,settlementService:SettlementService)->None:
        self._s3_service = s3_service
        self._parquet_service = parquet_service
        self._settlement_service = settlementService



    def export(self, file_id: str) -> str:
        start = time.perf_counter()
        parquet_path = f"/tmp/{file_id}.parquet"                                
        try:
            last_evaluated_key = None
            total_records = 0
            pages = 0

            self._parquet_service.start(parquet_path)

            while True:

                items, last_evaluated_key = (
                    self._settlement_service.get_settlements_paginated(
                        file_id=file_id,
                        limit=5000,
                        last_evaluated_key=last_evaluated_key
                    )
                )
                if items:
                    parquet_items = [
                        self.map_to_parquet(item)
                        for item in items
                    ]

                    self._parquet_service.write_batch(parquet_items)
                    total_records += len(items)
                    pages += 1
                    logger.debug("export_page_written", extra={
                        "page": pages,
                        "items": len(items),
                        "has_more": bool(last_evaluated_key),
                    })

                if not last_evaluated_key:
                    break

            self._parquet_service.close()

            if total_records == 0:
                logger.warning("export_empty", extra={"reason": "no_settlements_found"})

            self._s3_service.upload(
                bucket_name=BUCKET_NAME,
                route=parquet_path,
                name=f"{file_id}.parquet"
            )

            logger.info("export_finished", extra={
                "records_total": total_records,
                "pages": pages,
                "parquet_bytes": os.path.getsize(parquet_path) if os.path.exists(parquet_path) else 0,
                "duration_ms": int((time.perf_counter() - start) * 1000),
            })

            return file_id

        except Exception:
            logger.exception("export_failed")
            raise

        finally:                                                                 
            Path(parquet_path).unlink(missing_ok=True)                          


    def map_to_parquet(self,item: dict) -> dict:
        return {
            "settlement_id": item["SK"].replace("SETTLEMENT#", ""),
            "transaction_id": item["transaction_id"],
            "file_id": item["PK"].replace("FILE#", ""),
            "amount": float(item["settled_amount"]),
            "currency": item["currency"],
            "provider": item["provider_name"],
            "status": item["settlement_status"],
            "created_at": item["settlement_date"],
        }