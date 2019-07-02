vpc {
  type = "module"
  source = "github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v1.59.0"
  dependencies = ["foo"]
  inputs {
    name = "vpc-dev"
    enable_nat_gateway = false
    single_nat_gateway = false
    enable_dns_hostnames = true
    enable_dns_support = true
  }
  region_inputs {
    stuff = "things"
  }
}

{% raw %}
{% endraw %}

keys {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git//common/keys"
  dependencies = [""]
  inputs {
    name = "keys"
  }
}

security_groups {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git//common/keys"
  dependencies = ["stuff", "things"]
  inputs {
    name = "security_groups"
  }
}
