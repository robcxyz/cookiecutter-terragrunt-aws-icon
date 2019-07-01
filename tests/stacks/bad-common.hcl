vpc {
  type = "module"
//  source = "github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v1.59.0"
  dependencies = []
  vars {
    name = "vpc-dev"
    enable_nat_gateway = false
    single_nat_gateway = false
    enable_dns_hostnames = true
    enable_dns_support = true
  }
}

keys {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git//common/keys"
  dependencies = [""]
  vars {
    name = "keys"
  }
}

security_groups {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git//common/keys"
  //  source = "github.com/{ git_user }/{ repo }.git//{ module_path }"
  dependencies = [""]
  vars {
    name = "security_groups"
  }
{% endif %}