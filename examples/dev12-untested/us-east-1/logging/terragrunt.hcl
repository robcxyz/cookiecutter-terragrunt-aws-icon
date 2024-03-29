
terraform {
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/logging//logs"
  extra_arguments "custom_vars" {
    commands  = ["apply", "plan"]
    arguments = ["-var", "foo=42"]
  }
}

include {
  path = find_in_parent_folders()
}


inputs = {
  
  lb_logs_path = "lb-logs"
  name = "logs"
  s3_logs_path = "s3-logs"
  resource_group = "logs"
}