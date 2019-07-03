
terragrunt = {
  terraform {
    source = "github.com/robcxyz/terragrunt-root-modules.git/aws/compute//ec2"
  }
  include {
    path = "${find_in_parent_folders()}"
  }

  dependencies {
    paths = [
    "../vpc",
    "../ebs",
    "../efs",
    "../security_groups",
    "../keys"
    ]
  }
}


  
efs_directory = "/opt/data"
resource_group = "ec2"
volume_dir = ""
root_volume_size = "20"
instance_type = "m4.large"
volume_path = "/dev/sdf"
