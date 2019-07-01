vpc {
  type = "module"
  source = "github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v1.59.0"
  inputs {
    name = "vpc-dev"
    enable_nat_gateway = "false"
    single_nat_gateway = "false"
    enable_dns_hostnames = "true"
    enable_dns_support = "true"
    cidr = "{{ cookiecutter.cidr }}"
  }
  region_inputs {
    {% for k, v in networking.items() %}
    {{ k }} = "{{ v }}"{% endfor %}
  }
}

ec2 {
  type = "module"
  source = "github.com/robcxyz/terragrunt-aws-modules.git//compute/ec2?ref=v1.1.0"
  dependencies = [
    "vpc",
    "ebs"
  ]
  inputs {
    name = "ec2"
  }
}

ebs {
  type = "module"
  source = ""
  inputs {
    name = "ec2"
  }
}

logging {
  type = "module"
  source = ""
  inputs {
    name = "logs"
    resource_group = "logs"
    lb_logs_path = "lb-logs"
    s3_logs_path = "s3-logs"
    log_bucket_region = "us-east-1"
  }
}

