iam-terraform {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/init/iam-terraform"
  inputs {
    name = "TerraformIAM"
  }
  region_inputs {
    stuff = "things"
  }
}


iam-user {
  type = "module"
  source = "github.com/robcxyz/terragrunt-root-modules.git/aws/init/iam-user"
  inputs {
    name = "UserIAM"
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
  dependencies = [
    "stuff",
    "things"]
  inputs {
    name = "security_groups"
  }
}
