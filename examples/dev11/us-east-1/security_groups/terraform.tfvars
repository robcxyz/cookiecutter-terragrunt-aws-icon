
terragrunt = {
  terraform {
    source = "github.com/robcxyz/terragrunt-root-modules.git?ref=v0.0.0/aws/common//security_groups"
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


  
resource_group = "security_groups"
