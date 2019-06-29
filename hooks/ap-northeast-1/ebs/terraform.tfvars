terragrunt = {
  terraform {
    source = ""
  }

  include {
    path = "${find_in_parent_folders()}"
  }

  dependencies {
    paths = [

    "../ec2"
    ]
  }
}


