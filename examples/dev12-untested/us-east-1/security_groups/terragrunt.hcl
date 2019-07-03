
terraform {
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/common//security_groups"
  extra_arguments "custom_vars" {
    commands  = ["apply", "plan"]
    arguments = ["-var", "foo=42"]
  }
}

include {
  path = find_in_parent_folders()
}

dependencies {
  paths = [
  "../vpc"
  ]
}

inputs = {
  
  resource_group = "security_groups"
}