
terragrunt = {
  terraform {
    source = "github.com/robcxyz/terragrunt-root-modules.git/aws/storage//efs"
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


  
volume_path = "/dev/sdf"
resource_group = "efs"
