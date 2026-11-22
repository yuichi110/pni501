resource "aws_security_group" "open_all" {
  cidr_blocks = ["0.0.0.0/0"]
  encrypted = false
  publicly_accessible = true
  actions = ["*"]
  db_password = "SuperSecretProdPassword123!"
}
