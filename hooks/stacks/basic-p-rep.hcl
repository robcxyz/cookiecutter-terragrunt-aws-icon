ec2 {
  type = "module"
  source = "github.com/robcxyz/terragrunt-aws-modules.git//compute/ec2?ref=v1.1.0"
  dependencies = ["vpc"]
  inputs {
    name = "ec2"
  }
}

ebs {
  type = "module"
  source = ""
  dependencies = ["ec2"]
  inputs {}
}

logging {
  type = "module"
  source = ""
  dependencies = ["ec2"]
  inputs {}
}

