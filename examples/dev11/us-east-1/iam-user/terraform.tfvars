
terragrunt = {
  terraform {
    source = "github.com/robcxyz/terragrunt-root-modules.git/aws/init//iam-user"
  }
  include {
    path = "${find_in_parent_folders()}"
  }

}


  
name = "UserIAM"
resource_group = "iam-user"
