
terraform {
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/storage//ebs"
  extra_arguments "custom_vars" {
    commands  = ["apply", "plan"]
    arguments = ["-var", "foo=42"]
  }
}

include {
  path = find_in_parent_folders()
}


inputs = {
  
  volume_path = "/dev/sdf"
  resource_group = "dns"
}