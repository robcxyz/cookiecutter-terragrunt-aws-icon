terragrunt = {
  terraform {
    source = "github.com/robcxyz/terragrunt-aws-modules.git//compute/ec2?ref=v1.1.0"
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



name = ec2