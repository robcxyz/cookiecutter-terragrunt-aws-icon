vpc {
  type = "module"
  source = "github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v1.59.0"
  dependencies = []
  inputs {
    name = "vpc-dev"
    enable_nat_gateway = false
    single_nat_gateway = false
    enable_dns_hostnames = true
    enable_dns_support = true
  }
}

keysg {
  type = "module"
  source = ""
  dependencies = [""]
  inputs {
    name = "keys"
  }
}

security_groups {
  type = "module"
  source = ""
  dependencies = [""]
  inputs {
    name = "security_groups"
  }
}


