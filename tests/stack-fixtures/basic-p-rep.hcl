ec2 {
  type = "module"
  source = "github.com/{ git_user }/{ repo }.git//{{ module_path }}"
  dependencies = ["{ dependencies }"]
  vars {
    name = "ec2"
  }
}

ebs {
  type = "module"
  source = ""
  dependencies = []
  vars {}
}

logging {
  type = "module"
  source = ""
  dependencies = ["stuff", "things"]
  vars {}
}

