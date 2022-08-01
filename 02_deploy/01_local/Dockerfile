FROM python:3.8.12-slim

RUN pip install -U pip
RUN pip install -U scikit-learn==1.1.1 mlflow==1.27.0 gunicorn

WORKDIR /app
COPY artifacts/ ./artifacts/
COPY predict.py .

EXPOSE 9696

ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:9696", "predict:app" ]
