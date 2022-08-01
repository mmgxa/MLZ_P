import os

import mlflow
import numpy as np
from flask import Flask, jsonify, request

RUN_ID = os.getenv("RUN_ID")

# logged_model = f's3://mlopszc-project-artifacts/2/{RUN_ID}/artifacts/models'
logged_model = "artifacts/models"
model = mlflow.sklearn.load_model(logged_model)


def prepare_features(features):
    features = np.array(
        [[features["alcohol"], features["volatile acidity"], features["sulphates"]]]
    )
    return features


def predict(X):
    preds = model.predict(X)
    return preds[0]


app = Flask("wine-quality")


@app.route("/predict", methods=["POST"])
def predict_endpoint():
    ride = request.get_json()
    features = prepare_features(ride)
    pred = predict(features)

    result = {"quality": pred}

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
