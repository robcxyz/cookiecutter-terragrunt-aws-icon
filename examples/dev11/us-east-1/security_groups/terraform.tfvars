
terragrunt = {
  terraform {
    source = "github.com/robcxyz/terragrunt-root-modules.git/aws/common//security_groups"
  }
  include {
    path = "${find_in_parent_folders()}"
  }

  dependencies {
    paths = [
    "../vpc"
    ]
  }
}

inputs = {
  
  resource_group = "security_groups"
}