vpc {
  type = "module"
  source = "github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v1.59.0"
  inputs {
    name = "vpc-dev"
    enable_nat_gateway = "false"
    single_nat_gateway = "false"
    enable_dns_hostnames = "true"
    enable_dns_support = "true"
    cidr = "10.0.0.0/16"
  }
  region_inputs {
    azs = ["us-east-1a", "us-east-1b", "us-east-1c"]

    private_subnets = ["10.0.0.0/20", "10.0.16.0/20", "10.0.32.0/20"]
    public_subnets = ["10.0.64.0/20", "10.0.80.0/20", "10.0.96.0/20"]
  }
}

keys {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git/common/keys"
  inputs {
    name = "keys"
  }
}

security_groups {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git/common/keys"
  dependencies = ["stuff", "things"]
  inputs {
    name = "security_groups"
  }
}
