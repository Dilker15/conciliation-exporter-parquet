from services.exporter import ExporterService
from services.parquet_write_service import ParquetWriterService
from services.s3_service import S3Service
from services.settlement_service import SettlementService
from shared_layer.repositories.settlement_repository import SettlementRepository
from shared_layer.services.observability import get_logger                       
from datetime import datetime

logger = get_logger()                                                            

exporter_service = ExporterService(
                    parquet_service=ParquetWriterService(),
                    s3_service=S3Service(),
                    settlementService=SettlementService(repository=SettlementRepository())
                                   )


@logger.inject_lambda_context(log_event=False, clear_state=True)                 
def lambda_handler(event, context):

    file_id = event["detail"]["file_id"]
    key_file = event["detail"]["key_file"]
    logger.append_keys(file_id=file_id)                                          
    settlement_date = parse_date(key=key_file)
    logger.info("export_started", extra={                                        
        "key_file": key_file,
        "settlement_date": settlement_date.isoformat(),
    })
    result = exporter_service.export(file_id)

    return {
       "file_id": file_id,
       "settlement_date": settlement_date.isoformat()
    }



def parse_date(key:str)->datetime:
    parts = key.split("/")
    year = int(parts[0].split("=")[1])
    month = int(parts[1].split("=")[1])
    day = int(parts[2].split("=")[1])
    date = datetime(year, month, day)
    return date