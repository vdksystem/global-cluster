# VPC where TGW will be placed
data "aws_availability_zones" "available" {}
data "aws_region" "current" {}

locals {
  name   = "ex-${basename(path.cwd)}"
  region = "eu-west-1" # Our primary region
  # We are going to use this module to centrally manage VPC CIDRs
  ip_cidrs = {
    main = "10.1.0.0/16"  # Our main VPC for centralized networking
    prod_us-east_1 = "10.2.0.0/16"
    prod_us-west-1 = "10.3.0.0/16"
    tgw_ipv4_cidr_block = "10.99.0.0/24"
  }

  vpc_cidr = local.ip_cidrs.main
  azs = slice(data.aws_availability_zones.available.names, 0, 2)  # We need only two AZs for this example

  tags = {
    ManagedBy = "Terraform"
  }
}

################################################################################
# VPC Module
################################################################################

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "6.0.1"

  name = "main"
  cidr = local.vpc_cidr

  azs             = local.azs
  private_subnets = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k)]
  public_subnets  = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k + 4)]

  #   private_subnet_names = ["Private Subnet One", "Private Subnet Two"]
  # public_subnet_names omitted to show default name generation for all three subnets

  manage_default_network_acl    = false
  manage_default_route_table    = false
  manage_default_security_group = false

  enable_dns_hostnames = true
  enable_dns_support   = true

  enable_nat_gateway = true
  single_nat_gateway = true

  tags = local.tags
}

################################################################################
# VPC Endpoints Module
################################################################################

module "endpoints" {
  source  = "terraform-aws-modules/vpc/aws//modules/vpc-endpoints"
  version = "6.0.1"

  vpc_id                = module.vpc.vpc_id
  create_security_group = true

  endpoints = {
    s3 = {
      # interface endpoint
      service = "s3"
      tags = { Name = "s3-vpc-endpoint" }
    }
  }

  tags = merge(
    local.tags,
    {
      Stack = "test"
    }
  )
}

################################################################################
# VPC TGW
################################################################################
module "tgw" {
  source          = "terraform-aws-modules/transit-gateway/aws"
  version         = "2.13.0"
  name            = "main"
  description     = "Main company TGW"
  amazon_side_asn = 64532

  transit_gateway_cidr_blocks = [local.ip_cidrs.tgw_ipv4_cidr_block]

  enable_auto_accept_shared_attachments = false
  enable_sg_referencing_support = true

  enable_multicast_support = false

  tags = local.tags
}