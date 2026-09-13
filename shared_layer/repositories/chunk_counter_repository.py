import logging
from datetime import datetime, timezone
import boto3
import os
from botocore.exceptions import ClientError
from shared_layer.models.chunk_counter import ChunkCounterData

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ChunkCounterRepository:


    def __init__(self):
        self._db_client = boto3.client("dynamodb")
        self._table_name = os.environ["CHUNK_COUNTER_TABLE_NAME"]

    def create_chunk_counter(self, data: ChunkCounterData) -> None:
        item = {
            "file_id": {"S": data.file_id},
            "total_chunks": {"N": str(data.total_chunks)},
            "status": {"S": data.status},
            "created_at": {"S": data.created_at.isoformat()},
            "updated_at": {"S": data.updated_at.isoformat()},
        }   
        try:
            self._db_client.put_item(
                TableName=self._table_name,
                Item=item,
                ConditionExpression="attribute_not_exists(file_id)",
            )
        except ClientError as error:

            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.warning("Chunk counter ya existía para file_id=%s", data.file_id)
                return
            raise



    def register_chunk_processed(self, file_id: str, chunk_index: int) -> dict:
        try:
            response = self._db_client.update_item(
                TableName=self._table_name,
                Key={"file_id": {"S": file_id}},
                UpdateExpression=(
                    "ADD processed_chunk_indexes :chunk "
                    "SET updated_at = :now"
                ),
                ConditionExpression="attribute_exists(file_id)",  # <- clave
                ExpressionAttributeValues={
                    ":chunk": {"NS": [str(chunk_index)]},
                    ":now": {"S": datetime.now(timezone.utc).isoformat()},
                },
                ReturnValues="ALL_NEW",
            )
            return response["Attributes"]

        except ClientError as error:
            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.warning(
                    "chunk_index=%d llegó antes de que existiera el counter para file_id=%s "
                    "- se reintentará vía SQS",
                    chunk_index, file_id
                )
                raise  # importante: SÍ re-lanzar.

            logger.exception(
                "Error registrando chunk_index=%d para file_id=%s", chunk_index, file_id
            )
            raise


    def mark_completed(self, file_id: str) -> None:
        try:
            self._db_client.update_item(
                TableName=self._table_name,
                Key={"file_id": {"S": file_id}},
                UpdateExpression="SET #status = :completed, updated_at = :now",
                ConditionExpression="#status = :processing",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":completed": {"S": "COMPLETED"},
                    ":processing": {"S": "PROCESSING"},
                    ":now": {"S": datetime.now(timezone.utc).isoformat()},
                },
            )
        except ClientError as error:
            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.warning("file_id=%s ya no estaba en PROCESSING", file_id)
                return
            raise