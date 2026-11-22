# Terraform resources for Shipment domain

resource "aws_s3_bucket" "shipment_bucket_1" {
  bucket = "sample-shipment-data-1"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "shipping"
    Environment = "prod"
    Index       = "1"
  }
}

resource "aws_s3_bucket" "shipment_bucket_2" {
  bucket = "sample-shipment-data-2"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "shipping"
    Environment = "prod"
    Index       = "2"
  }
}

resource "aws_s3_bucket" "shipment_bucket_3" {
  bucket = "sample-shipment-data-3"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "shipping"
    Environment = "prod"
    Index       = "3"
  }
}

resource "aws_s3_bucket" "shipment_bucket_4" {
  bucket = "sample-shipment-data-4"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "shipping"
    Environment = "prod"
    Index       = "4"
  }
}

resource "aws_s3_bucket" "shipment_bucket_5" {
  bucket = "sample-shipment-data-5"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "shipping"
    Environment = "prod"
    Index       = "5"
  }
}

resource "aws_s3_bucket" "shipment_bucket_6" {
  bucket = "sample-shipment-data-6"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "shipping"
    Environment = "prod"
    Index       = "6"
  }
}

resource "aws_s3_bucket" "shipment_bucket_7" {
  bucket = "sample-shipment-data-7"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "shipping"
    Environment = "prod"
    Index       = "7"
  }
}

resource "aws_s3_bucket" "shipment_bucket_8" {
  bucket = "sample-shipment-data-8"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "shipping"
    Environment = "prod"
    Index       = "8"
  }
}

resource "aws_s3_bucket" "shipment_bucket_9" {
  bucket = "sample-shipment-data-9"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "shipping"
    Environment = "prod"
    Index       = "9"
  }
}

resource "aws_s3_bucket" "shipment_bucket_10" {
  bucket = "sample-shipment-data-10"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "shipping"
    Environment = "prod"
    Index       = "10"
  }
}
