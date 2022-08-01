#########################
#### IAM Role for Lambda
#########################

resource "aws_iam_role" "iam_lambda" {
  name = "iam_lambda_stg"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": [
          "lambda.amazonaws.com",
          "kinesis.amazonaws.com"
          ]
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

#####################################################
#### Create Policy for IAM Role for Lambda
#### Policy: Read from Kinesis Stream
#####################################################
resource "aws_iam_policy" "allow_kinesis_processing" {
  name        = "allow_kinesis_processing_${var.lambda_function_name}"
  path        = "/"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "kinesis:ListShards",
        "kinesis:ListStreams",
        "kinesis:*"
      ],
      "Resource": "arn:aws:kinesis:*:*:*",
      "Effect": "Allow"
    },
    {
      "Action": [
        "stream:GetRecord",
        "stream:GetShardIterator",
        "stream:DescribeStream",
        "stream:*"
      ],
      "Resource": "${var.source_stream_arn}",
      "Effect": "Allow"
    }
  ]
}
EOF
}


#####################################################
#### Attach created Policy for IAM Role for Lambda
#####################################################
resource "aws_iam_role_policy_attachment" "kinesis_processing" {
  role       = aws_iam_role.iam_lambda.name
  policy_arn = aws_iam_policy.allow_kinesis_processing.arn
}


#####################################################
#### Create Inline Policy for IAM Role for Lambda
#### Policy: Write to Kinesis Stream
#####################################################
resource "aws_iam_role_policy" "inline_lambda_policy" {
  name       = "LambdaInlinePolicy"
  role       = aws_iam_role.iam_lambda.id
  depends_on = [aws_iam_role.iam_lambda]
  policy     = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kinesis:PutRecords",
        "kinesis:PutRecord"
      ],
      "Resource": "${var.output_stream_arn}"
    }
  ]
}
EOF
}

#####################################################
#### Create Policy for CloudWatch To
####       Trigger the Lambda Function
#####################################################
# IAM for CW

resource "aws_lambda_permission" "allow_cloudwatch_to_trigger_lambda_function" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.kinesis_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = var.source_stream_arn
}

#####################################################
#### Create Policy for Lambda To
####       Log in CloudWatch
#####################################################
resource "aws_iam_policy" "allow_logging" {
  name        = "allow_logging_${var.lambda_function_name}"
  path        = "/"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

#####################################################
#### Attach Created Policy for Lambda To
####       Log in CloudWatch
#####################################################
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.iam_lambda.name
  policy_arn = aws_iam_policy.allow_logging.arn
}


#####################################################
#### Create Policy for Lambda To
####       Read Model from S3
#####################################################

resource "aws_iam_policy" "lambda_s3_role_policy" {
  name = "lambda_s3_policy_${var.lambda_function_name}"
  description = "IAM Policy for s3"
  # TODO: change policies below to reflect get operation
policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:GetBucketLocation",
                "s3:*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::${var.model_bucket}",
                "arn:aws:s3:::${var.model_bucket}/*"
            ]
        },
        {
          "Action": [
            "autoscaling:Describe*",
            "cloudwatch:*",
            "logs:*",
            "sns:*"
          ],
          "Effect": "Allow",
          "Resource": "*"
        }
  ]
}
  EOF
}

#####################################################
#### Attach Created Policy for Lambda To
####       Read Model from S3
#####################################################
resource "aws_iam_role_policy_attachment" "iam-policy-attach" {
  role       = aws_iam_role.iam_lambda.name
  policy_arn = aws_iam_policy.lambda_s3_role_policy.arn
}
