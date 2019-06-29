terragrunt = {
  terraform {
    source = "github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v1.59.0"
  }

  include {
    path = "${find_in_parent_folders()}"
  }

  dependencies {
    paths = [

    ]
  }
}



name = vpc-dev
enable_nat_gateway = False
single_nat_gateway = False
enable_dns_hostnames = True
enable_dns_support = True