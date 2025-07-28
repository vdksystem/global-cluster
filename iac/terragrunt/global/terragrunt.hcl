terraform {
  source = "${get_repo_root()}/iac/terraform/global"
}

include "root" {
  path = find_in_parent_folders("root.hcl")
  expose = true
}

include "env" {
  path = find_in_parent_folders("env.hcl")
  expose = true
}

inputs = {
  env         = include.env.locals.env
  domain_name = "test.adimen.tech"
}
