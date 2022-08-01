# Create Kinesis Data Stream

resource "aws_kinesis_stream" "stream" {
  name = var.stream_name
  shard_count = var.shard_count
  retention_period = var.retention_period
  stream_mode_details {
    stream_mode = "PROVISIONED"
  }
  tags = {
    "CreatedBy" = var.tags
  }
}

# return a value after a module is created
output "stream_arn" {
  value = aws_kinesis_stream.stream.arn
}
