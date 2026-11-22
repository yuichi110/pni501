# Terraform resources for LedgerEntry domain

resource "aws_s3_bucket" "ledger_bucket_1" {
  bucket = "sample-ledger-data-1"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "ledger"
    Environment = "prod"
    Index       = "1"
  }
}

resource "aws_s3_bucket" "ledger_bucket_2" {
  bucket = "sample-ledger-data-2"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "ledger"
    Environment = "prod"
    Index       = "2"
  }
}

resource "aws_s3_bucket" "ledger_bucket_3" {
  bucket = "sample-ledger-data-3"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "ledger"
    Environment = "prod"
    Index       = "3"
  }
}

resource "aws_s3_bucket" "ledger_bucket_4" {
  bucket = "sample-ledger-data-4"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "ledger"
    Environment = "prod"
    Index       = "4"
  }
}

resource "aws_s3_bucket" "ledger_bucket_5" {
  bucket = "sample-ledger-data-5"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "ledger"
    Environment = "prod"
    Index       = "5"
  }
}

resource "aws_s3_bucket" "ledger_bucket_6" {
  bucket = "sample-ledger-data-6"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "ledger"
    Environment = "prod"
    Index       = "6"
  }
}

resource "aws_s3_bucket" "ledger_bucket_7" {
  bucket = "sample-ledger-data-7"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "ledger"
    Environment = "prod"
    Index       = "7"
  }
}

resource "aws_s3_bucket" "ledger_bucket_8" {
  bucket = "sample-ledger-data-8"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "ledger"
    Environment = "prod"
    Index       = "8"
  }
}

resource "aws_s3_bucket" "ledger_bucket_9" {
  bucket = "sample-ledger-data-9"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "ledger"
    Environment = "prod"
    Index       = "9"
  }
}

resource "aws_s3_bucket" "ledger_bucket_10" {
  bucket = "sample-ledger-data-10"
  acl    = "private"
  versioning {
    enabled = true
  }
  tags = {
    Domain      = "ledger"
    Environment = "prod"
    Index       = "10"
  }
}
