data "aws_caller_identity" "current" {}
data "aws_region" "current" {}


resource "aws_key_pair" "global_admins" {
  key_name   = "global_admins"
  public_key = var.public_key
}
