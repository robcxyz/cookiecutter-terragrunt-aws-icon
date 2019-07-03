iam-terraform {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/init//iam-terraform"
  inputs {
    name = "TerraformIAM"
  }
}

iam-user {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/init//iam-user"
  inputs {
    name = "UserIAM"
  }
}

keys {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/common//keys"
  inputs {
    name = "keys"
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
