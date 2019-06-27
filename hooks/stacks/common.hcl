vpc {
  type = "module"
  source = "github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v1.59.0"
  requires = ""
  dependencies = ""
  vars {
    name = "vpc-dev"
    enable_nat_gateway = false
    single_nat_gateway = false
    enable_dns_hostnames = true
    enable_dns_support = true
  }
}

keys {
  source = "github.com/{ git_user }/{ repo }.git//{ module_path }"
  requires = ""
  dependencies = ""
  vars {
    name = "keys"
  }
}

security_groups {
  source = "github.com/{ git_user }/{ repo }.git//{ module_path }"
  requires = ""
  dependencies = ""
  vars {
    name = "security_groups"
  }
}
