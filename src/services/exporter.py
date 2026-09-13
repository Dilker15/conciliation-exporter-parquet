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
            next_key = None
            parquet_path = f"/tmp/{file_id}.parquet"

            self._parquet_service.start(parquet_path)

            while True:

                items, next_key = (self._settlement_service.get_settlements_paginated(
                                                                                    file_id=file_id,
                                                                                    limit=5000,
                                                                                    last_evaluated_key=next_key)
                                    )
                if items:
                    self._parquet_service.write_batch(items)

                if not next_key:
                    break

            self._parquet_service.close()

            self._s3_service.upload(bucket_name=BUCKET_NAME,route=parquet_path,name=f"{file_id}.parquet")

            return file_id

        except Exception as error:
            print(f"Error on Export: {error}")
            raise


