variable "aws_region" {
  description = "AWS region to create resources"
  default = "us-east-2"
}

variable "project_id" {
  description = "id of project to group our resources"
  default = "mlops-proj"
}

variable "source_stream_name" {
  description = "name of our source kinesis stream"
}

variable "output_stream_name" {
  description = "name of our output kinesis stream"
}

variable "model_bucket" {
  description = "name of our model s3 bucket"
}

variable "lambda_function_local_path" {
  description = "path to our local lambda_function.py file"
}

variable "docker_image_local_path" {
  description = "path to our local docker file"
}

variable "ecr_repo_name" {
  description = "name of our ecr repo"
}

variable "lambda_function_name" {
  description = "name of our lambda function"
}

variable "run_id" {
  description = "RUN ID for the best logged model"
}

variable "test_run" {
  description = "whether or not this is a test run"
}
