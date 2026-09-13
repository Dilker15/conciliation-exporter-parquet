import boto3
from boto3.dynamodb.types import TypeSerializer

from shared_layer.models.settlement_errors import SettlementError
import os

class SettlementErrorRespository:

    def __init__(self):
        self._client = boto3.client("dynamodb")
        self._serializer = TypeSerializer()
        self._table_name = os.environ["CONCILIATION_TABLE_NAME"]


    def create_settlement_error_batch(self,settlement_errors: list[SettlementError]):
        requests = []

        for settlement_error in settlement_errors:
            requests.append({
                "PutRequest": {
                    "Item": {
                        "PK": {
                            "S": f"FILE#{settlement_error.file_id}"
                        },
                        "SK": {
                            "S": f"ERROR#{settlement_error.row_number}"
                        },
                        "row_number": {
                            "N": str(settlement_error.row_number)
                        },
                        "errors": {
                            "L": [
                                {
                                    "S": error
                                }
                                for error in settlement_error.errors
                            ]
                        },
                        "raw_data": self._serializer.serialize(
                            settlement_error.raw_data
                        )
                    }
                }
            })

        self._client.batch_write_item(
            RequestItems={
                self._table_name: requests
            }
        )

