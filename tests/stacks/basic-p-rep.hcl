ec2 {
  type = "module"
  source = "github.com/{ git_user }/{ repo }.git//{{ module_path }}"
  dependencies = ["{ dependencies }"]
  inputs {
    name = "ec2"
  }
}

ebs {
  type = "module"
  source = ""
  dependencies = []
  inputs {}
}

logging {
  type = "module"
  source = ""
  dependencies = ["stuff", "things"]
  inputs {}
}

