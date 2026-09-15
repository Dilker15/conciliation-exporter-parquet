import boto3



class S3Service:


    def __init__(self)->None:
        self._client = boto3.client("s3")
  


    def upload(self,bucket_name:str,route:str,name:str):

        self._client.upload_file(Bucket=bucket_name,
                                 Key=f"settlements/{name}",
                                 Filename=route
                                )


