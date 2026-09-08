import json

def lambda_handler(event, context):
    # TODO implement
    print("lambda executed succesfully with eventbridge")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda exporter, this lambda was processed by event_bridge')
    }
