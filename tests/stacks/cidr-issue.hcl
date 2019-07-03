vpc {
  type = "module"
  source = "github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v1.59.0"
  inputs {
    name = "vpc-dev"
    enable_nat_gateway = "false"
    single_nat_gateway = "false"
    enable_dns_hostnames = "true"
    enable_dns_support = "true"
  }
  region_inputs {
    azs = ["us-east-1a", "us-east-1b", "us-east-1c"]
    cidr = "10.0.0.0/16"
    private_subnets = ["10.10.0.0/20", "10.10.16.0/20", "10.10.32.0/20"]
    public_subnets = ["10.10.64.0/20", "10.10.80.0/20", "10.10.96.0/20"]
  }
}