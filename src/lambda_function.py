from services.exporter import ExporterService
from services.parquet_write_service import ParquetWriterService
from services.s3_service import S3Service
from services.settlement_service import SettlementService
from shared_layer.repositories.settlement_repository import SettlementRepository
from datetime import datetime

exporter_service = ExporterService(
                    parquet_service=ParquetWriterService(),
                    s3_service=S3Service(),
                    settlementService=SettlementService(repository=SettlementRepository())
                                   )


def lambda_handler(event, context):

    file_id = event["detail"]["file_id"]
    key_file = event["detail"]["key_file"]
    settlement_date = parse_date(key=key_file)
    result = exporter_service.export(file_id)

    return {
        "result": result,
        "settlement_date": settlement_date.isoformat()
    }

def parse_date(key:str)->datetime:
    parts = key.split("/")
    year = int(parts[0].split("=")[1])
    month = int(parts[1].split("=")[1])
    day = int(parts[2].split("=")[1])
    date = datetime(year, month, day)
    return date