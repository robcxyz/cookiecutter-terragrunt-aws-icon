iam-terraform {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/init//iam-terraform"
  inputs {
    resource_group = "iam-terraform"
    name = "TerraformIAM"
  }
}

iam-user {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/init//iam-user"
  inputs {
    resource_group = "iam-user"
    name = "UserIAM"
  }
}

keys {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/common//keys"
  inputs {
    name = "keys"
    resource_group = "keys"
  }
}

security_groups {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/common//security_groups"
  dependencies = ["vpc"]
  inputs {
    resource_group = "security_groups"
  }
}
