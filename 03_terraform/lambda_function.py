import base64
import json
import os

import boto3
import mlflow
import numpy as np

RUN_ID = os.getenv("RUN_ID")


logged_model = f"s3://mlopszc-project-artifacts/2/{RUN_ID}/artifacts/models"
model = mlflow.sklearn.load_model(logged_model)


kinesis_client = boto3.client("kinesis", region_name="us-east-2")

PREDICTIONS_STREAM_NAME = os.getenv("PREDICTIONS_STREAM_NAME", "mlops-proj-predict")
TEST_RUN = os.getenv("TEST_RUN", "False") == "True"


def prepare_features(features):
    features = np.array(
        [[features["alcohol"], features["volatile acidity"], features["sulphates"]]]
    )
    return features


def predict(X):
    preds = model.predict(X)
    return preds[0]


def lambda_handler(event, context):

    predictions_events = []

    for record in event["Records"]:
        encoded_data = record["kinesis"]["data"]
        decoded_data = base64.b64decode(encoded_data).decode("utf-8")
        ride_event = json.loads(decoded_data)

        wine_features = ride_event["wine_features"]
        customer_id = ride_event["customer_id"]

        features = prepare_features(wine_features)
        prediction = predict(features)

        prediction_event = {
            "model": "wine_quality_prediction_model",
            "version": "2",
            "prediction": {"wine_quality": prediction, "customer_id": customer_id},
        }

        print(TEST_RUN)
        if not TEST_RUN:
            kinesis_client.put_record(
                StreamName=PREDICTIONS_STREAM_NAME,
                Data=json.dumps(prediction_event),
                PartitionKey=str(customer_id),
            )

        predictions_events.append(prediction_event)

    return {"predictions": predictions_events}
