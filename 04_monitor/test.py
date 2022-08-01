import requests

url = "http://127.0.0.1:9696/predict"

features = {"alcohol": 8.8, "volatile acidity": 0.27, "sulphates": 0.45}


response = requests.post(url, json=features).json()
print(response)
