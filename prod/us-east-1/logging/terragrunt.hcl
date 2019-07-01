
terraform {
  source = ""
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
  log_bucket_region = "us-east-1"
  name = "logs"
  s3_logs_path = "s3-logs"
  resource_group = "logs"
}