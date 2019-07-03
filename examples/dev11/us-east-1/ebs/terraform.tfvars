
terragrunt = {
  terraform {
    source = "github.com/robcxyz/terragrunt-root-modules.git/aws/storage//ebs"
  }
  include {
    path = "${find_in_parent_folders()}"
  }

}


  
volume_path = "/dev/sdf"
resource_group = "ebs"
ebs_volume_size = 100