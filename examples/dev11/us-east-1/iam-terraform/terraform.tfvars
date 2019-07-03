
terragrunt = {
  terraform {
    source = "github.com/robcxyz/terragrunt-root-modules.git/aws/init//iam-terraform"
  }
  include {
    path = "${find_in_parent_folders()}"
  }

}

inputs = {
  
  name = "TerraformIAM"
}