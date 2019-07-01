
terraform {
  source = "github.com/robcxyz/terragrunt-aws-modules.git//compute/ec2?ref=v1.1.0"
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
  "../vpc",
  "../ebs"
  ]
}

inputs = {
  
  name = "ec2"
}