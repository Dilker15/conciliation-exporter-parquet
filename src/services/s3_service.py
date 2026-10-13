import time                                                                      
import boto3
from shared_layer.services.observability import get_logger                      

logger = get_logger()                                                           


class S3Service:


    def __init__(self)->None:
        self._client = boto3.client("s3")



    def upload(self,bucket_name:str,route:str,name:str):

        start = time.perf_counter()                                              
        self._client.upload_file(Bucket=bucket_name,
                                 Key=f"settlements/{name}",
                                 Filename=route
                                )
        logger.info("parquet_uploaded", extra={                                 
            "bucket": bucket_name,
            "key": f"settlements/{name}",
            "duration_ms": int((time.perf_counter() - start) * 1000),
        })