terraform {
  required_version = ">= 1.0"
  backend "local" {}
}

provider "aws" {
  region = var.aws_region
  profile = "default"
}


data "aws_caller_identity" "current_identity" {}

locals {
  account_id = data.aws_caller_identity.current_identity.account_id
}

# 'Input' Kinesis Stream
module "source_kinesis_stream" {
  source = "./modules/kinesis"
  stream_name = "${var.source_stream_name}_${var.project_id}"
  retention_period = 24
  shard_count = 1
  tags = var.project_id
}

# 'Output' Kinesis Stream
module "output_kinesis_stream" {
  source = "./modules/kinesis"
  stream_name = "${var.output_stream_name}_${var.project_id}"
  retention_period = 24
  shard_count = 1
  tags = var.project_id
}

# image registry
module "ecr_image" {
   source = "./modules/ecr"
   ecr_repo_name = "${var.ecr_repo_name}_${var.project_id}"
   account_id = local.account_id
   lambda_function_local_path = var.lambda_function_local_path
   docker_image_local_path = var.docker_image_local_path
}

module "lambda_function" {
  source = "./modules/lambda"
  image_uri = module.ecr_image.image_uri
  lambda_function_name = "${var.lambda_function_name}_${var.project_id}"
  model_bucket = var.model_bucket
  output_stream_name = "${var.output_stream_name}_${var.project_id}"
  output_stream_arn = module.output_kinesis_stream.stream_arn
  source_stream_name = "${var.source_stream_name}_${var.project_id}"
  source_stream_arn = module.source_kinesis_stream.stream_arn
  run_id = var.run_id
  test_run = var.test_run
  depends_on = [module.source_kinesis_stream, module.output_kinesis_stream, module.ecr_image]
}
