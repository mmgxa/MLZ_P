import requests

features = {"alcohol": 8.8, "volatile acidity": 0.27, "sulphates": 0.45}

url = "http://127.0.0.1:9696/predict"
response = requests.post(url, json=features)
print(response.json())
