
terragrunt = {
  terraform {
    source = "github.com/robcxyz/terragrunt-root-modules.git/aws/storage//ebs"
  }
  include {
    path = "${find_in_parent_folders()}"
  }

}

inputs = {
  
  volume_path = "/dev/sdf"
  resource_group = "dns"
}