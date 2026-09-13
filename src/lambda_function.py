from services.exporter import ExporterService
from services.parquet_write_service import ParquetWriterService
from services.s3_service import S3Service
from services.settlement_service import SettlementService
from shared_layer.repositories.settlement_repository import SettlementRepostory

exporter_service = ExporterService(
                    parquet_service=ParquetWriterService(),
                    s3_service=S3Service(),
                    settlementService=SettlementService(repository=SettlementRepostory())
                                   )


def lambda_handler(event, context):

    file_id = event["detail"]["file_id"]
    result = exporter_service.export(file_id)
    return {
        "statusCode": 200,
        "body": result
    }