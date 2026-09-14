import boto3
from shared_layer.models.settlement import Settlement
import os
from typing import Any

class SettlementRepository:

    def __init__(self):
        self._client = boto3.client("dynamodb")
        self._table_name = os.environ["CONCILIATION_TABLE_NAME"]

    def create_settlement_batch(self, settlements: list[Settlement]):
        requests = []

        for settlement in settlements:
            requests.append({
                "PutRequest": {
                    "Item": {
                        "PK": {
                            "S": f"FILE#{settlement.file_id}"
                        },
                        "SK":{
                            "S":f"SETTLEMENT#{settlement.settlement_id}"
                        },
                        "transaction_id": {
                            "S": settlement.transaction_id
                        },
                        "provider_name": {
                            "S": settlement.provider_name
                        },
                        "settled_amount": {
                            "N": str(settlement.settled_amount)
                        },
                        "currency": {
                            "S": settlement.currency
                        },
                        "settlement_status": {
                            "S": settlement.settlement_status
                        },
                        "settlement_date": {
                            "S": settlement.settlement_date.isoformat()
                        }
                    }
                }
            })

        response = self._client.batch_write_item(
            RequestItems={
                self._table_name: requests
            }
        )


    def get_settlements_paginated(self,file_id: str,limit: int = 5000,last_evaluated_key: dict[str, Any] | None = None) -> tuple[list[dict], dict | None]:
        params = {
            "TableName": self._table_name,
            "KeyConditionExpression": "PK = :pk AND begins_with(SK, :sk)",
            "ExpressionAttributeValues": {
                ":pk": {
                    "S": f"FILE#{file_id}"
                },
                ":sk": {
                    "S": "SETTLEMENT#"
                }
            },
            "Limit": limit
        }

        if last_evaluated_key:
            params["ExclusiveStartKey"] = last_evaluated_key

        response = self._client.query(**params)

        return (
            response.get("Items", []),
            response.get("LastEvaluatedKey")
        )