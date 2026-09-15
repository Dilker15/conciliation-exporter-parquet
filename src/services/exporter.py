from services.parquet_write_service import ParquetWriterService
from services.s3_service import S3Service
from services.settlement_service import SettlementService
import os


BUCKET_NAME = os.environ["BUCKET_NAME"]

class ExporterService:


    def __init__(self,s3_service:S3Service,parquet_service:ParquetWriterService,settlementService:SettlementService)->None:
        self._s3_service = s3_service
        self._parquet_service = parquet_service
        self._settlement_service = settlementService
        


    def export(self, file_id: str) -> str:
        try:
            last_evaluated_key = None

            parquet_path = f"/tmp/{file_id}.parquet"

            self._parquet_service.start(parquet_path)

            print("PAGINATION STARTED")

            while True:
                print("LOOP STARTED")

                items, last_evaluated_key = (
                    self._settlement_service.get_settlements_paginated(
                        file_id=file_id,
                        limit=5000,
                        last_evaluated_key=last_evaluated_key
                    )
                )
                print("---------- ITEMS QUERY --------------")
                print(items)
                print("---------- ITEMS QUERY --------------")
                if items:
                    parquet_items = [
                        self.map_to_parquet(item)
                        for item in items
                    ]

                    self._parquet_service.write_batch(parquet_items)

                if not last_evaluated_key:
                    break

            self._parquet_service.close()

            print("PYARROW CLOSE")

            self._s3_service.upload(
                bucket_name=BUCKET_NAME,
                route=parquet_path,
                name=f"{file_id}.parquet"
            )

            return file_id

        except Exception as error:
            print(f"Error on Export: {error}")
            raise


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

