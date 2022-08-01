import os

import mlflow
import numpy as np
import requests
from flask import Flask, jsonify, request
from pymongo import MongoClient

logged_model = "artifacts/models"
model = mlflow.sklearn.load_model(logged_model)

EVIDENTLY_SERVICE_ADDRESS = os.getenv("EVIDENTLY_SERVICE", "http://127.0.0.1:5000")
MONGODB_ADDRESS = os.getenv("MONGODB_ADDRESS", "mongodb://127.0.0.1:27017")


app = Flask("quality")
mongo_client = MongoClient(MONGODB_ADDRESS)
db = mongo_client.get_database("prediction_service")
collection = db.get_collection("data")


@app.route("/predict", methods=["POST"])
def predict():
    record = request.get_json()

    features = np.array(
        [[record["alcohol"], record["volatile acidity"], record["sulphates"]]]
    )
    y_pred = model.predict(features)

    result = {
        "quality": y_pred[0],
    }

    save_to_db(record, y_pred[0])
    send_to_evidently_service(record, y_pred[0])
    return jsonify(result)


def save_to_db(record, quality):
    rec = record.copy()
    rec["quality"] = quality
    collection.insert_one(rec)


def send_to_evidently_service(record, quality):
    rec = record.copy()
    rec["quality"] = quality
    requests.post(f"{EVIDENTLY_SERVICE_ADDRESS}/iterate/wine", json=[rec])


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
