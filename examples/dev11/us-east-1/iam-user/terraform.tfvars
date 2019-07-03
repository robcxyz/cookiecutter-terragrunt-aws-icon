
terragrunt = {
  terraform {
    source = "github.com/robcxyz/terragrunt-root-modules.git/aws/init//iam-user"
  }
  include {
    path = "${find_in_parent_folders()}"
  }

}

inputs = {
  
  name = "UserIAM"
}