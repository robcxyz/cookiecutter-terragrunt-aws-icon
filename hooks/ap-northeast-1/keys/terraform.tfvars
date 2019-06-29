terragrunt = {
  terraform {
    source = "github.com/robcxyz/terragrunt-root-modules.git//common/keys"
  }

  include {
    path = "${find_in_parent_folders()}"
  }

  dependencies {
    paths = [

    "../"
    ]
  }
}



name = keys