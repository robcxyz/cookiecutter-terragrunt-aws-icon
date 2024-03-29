
terraform {
  source = "github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v1.59.0"
  extra_arguments "custom_vars" {
    commands  = ["apply", "plan"]
    arguments = ["-var", "foo=42"]
  }
}

include {
  path = find_in_parent_folders()
}


inputs = {
  
  enable_nat_gateway = "false"
  single_nat_gateway = "false"
  name = "vpc-dev"
  enable_dns_hostnames = "true"
  enable_dns_support = "true"
}