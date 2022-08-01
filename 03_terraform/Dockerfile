FROM public.ecr.aws/lambda/python:3.8

RUN pip install -U pip
RUN pip install -U scikit-learn==1.1.1 mlflow==1.27.0 boto3

COPY ["lambda_function.py", "./"]

CMD [ "lambda_function.lambda_handler"]
