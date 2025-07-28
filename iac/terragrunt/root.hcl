locals {
  # Automatically load environment-level variables
  env_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  account_id = local.env_vars.locals.aws_account_id
  # Extract the variables we need for easy access
  aws_region = "us-west-1"
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "${local.aws_region}"
}
EOF
}

remote_state {
  backend = "s3"
  config = {
    bucket  = "terraform-${local.account_id}"
    encrypt = true
    key     = "${path_relative_to_include()}/terraform.tfstate"
    region  = local.aws_region
  }
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
}
