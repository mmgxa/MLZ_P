import json
import uuid
from datetime import datetime
from time import sleep

# import pyarrow.parquet as pq
import pandas as pd
import requests

data = pd.read_csv("winequality-white.csv", delimiter=";")
data = data.to_dict("records")


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


with open("target.csv", "w") as f_target:
    for row in data:
        row["id"] = str(uuid.uuid4())
        f_target.write(f"{row['id']},{row['quality']}\n")
        resp = requests.post(
            "http://127.0.0.1:9696/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(row, cls=DateTimeEncoder),
        ).json()
        print(f"prediction: {resp['quality']}")
        sleep(1)
