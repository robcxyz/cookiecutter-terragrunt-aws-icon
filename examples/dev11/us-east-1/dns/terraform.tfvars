
terragrunt = {
  terraform {
    source = "github.com/robcxyz/terragrunt-root-modules.git/aws/networking//dns"
  }
  include {
    path = "${find_in_parent_folders()}"
  }

}

