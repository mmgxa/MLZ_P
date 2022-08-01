variable "stream_name" {
  description = "Kinesis stream name"
  type = string
}

variable "shard_count" {
  description = "Kinesis stream shard count"
  type = number
}

variable "retention_period" {
  description = "Kinesis stream retention period"
  type = number
}

variable "tags" {
  description = "Tags for Kinesis stream"
  default = "mlops-proj"
}
