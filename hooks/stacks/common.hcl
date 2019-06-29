vpc {
  type = "module"
  source = "github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v1.59.0"
  dependencies = []
  variables {
    name = "vpc-dev"
    enable_nat_gateway = false
    single_nat_gateway = false
    enable_dns_hostnames = true
    enable_dns_support = true
  }
  variables_environment {

  }
  region_variables {

  }
}

keys {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git//common/keys"
  dependencies = [""]
  variables {
    name = "keys"
  }
}

security_groups {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git//common/keys"
  //  source = "github.com/{ git_user }/{ repo }.git//{ module_path }"
  dependencies = [""]
  variables {
    name = "security_groups"
  }
}


