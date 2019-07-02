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
    private_subnets = [
      "10.10.0.0/20",
      "10.10.16.0/20",
      "10.10.32.0/20"]
    public_subnets = ["10.10.64.0/20", "10.10.80.0/20", "10.10.96.0/20"]
  }
  env_inputs {
  }
}

dns {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/networking//dns"
  inputs {
  }
  env_inputs {
    icon_domain_name = "solidwallet.io"
    node_subdomain = "net"
    tracker_subdomain = "tracker"
    root_domain_name = "solidwallet.io"
    org_subdomain = "insight"
  }
}


ec2 {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/compute//ec2"
  dependencies = [
    "vpc",
    "ebs",
    "efs",
    "security_groups",
    "keys"
  ]
  inputs {
    resource_group = "ec2"
    instance_type = "m4.large"
    root_volume_size = 20
    volume_path = "/dev/sdf"
    volume_dir = ""
    efs_directory = "/opt/data"
  }
}

ebs {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/storage//ebs"
  inputs {
    resource_group = "dns"
    volume_path = "/dev/sdf"

  }
  region_inputs {

  }
}

logging {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/logging//logs"
  inputs {
    resource_group = "logs"
    name = "logs"
    lb_logs_path = "lb-logs"
    s3_logs_path = "s3-logs"
  }
  env_inputs {
    log_bucket_region = "us-east-1"
    log_bucket = ""
    log_location_prefix = "logs"
  }
}

