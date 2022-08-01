import lambda_function

event = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49630081666084879290581185630324770398608704880802529282",
                "data": "ewogICAgIndpbmVfZmVhdHVyZXMiOiB7CiAgICAgICAgImFsY29ob2wiOiA4LjgsCiAgICAgICAgInZvbGF0aWxlIGFjaWRpdHkiOiAwLjI3LAogICAgICAgICJzdWxwaGF0ZXMiOiAwLjQ1CiAgICB9LCAKICAgICJjdXN0b21lcl9pZCI6IDEyMwp9Cg==",
                "approximateArrivalTimestamp": 1654161514.132,
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49630081666084879290581185630324770398608704880802529282",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::410330524497:role/mlops-proj-lambda-role",
            "awsRegion": "us-east-2",
            "eventSourceARN": "arn:aws:kinesis:us-east-2:410330524497:stream/mlops-proj-input",
        }
    ]
}


result = lambda_function.lambda_handler(event, None)
print(result)
