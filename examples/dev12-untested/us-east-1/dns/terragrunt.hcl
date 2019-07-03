
terraform {
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/networking//dns"
  extra_arguments "custom_vars" {
    commands  = ["apply", "plan"]
    arguments = ["-var", "foo=42"]
  }
}

include {
  path = find_in_parent_folders()
}


