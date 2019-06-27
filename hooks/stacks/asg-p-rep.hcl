asg {
  type = "module"
  source = "github.com/{ git_user }/{ repo }.git//{{ module_path }}"
  dependencies = "{ dependencies }"
  vars {
    name = "ec2"
  }
}

alb {
  type = "module"
  source = ""
  dependencies = ""
  vars {}
}

logging {
  type = "module"
  source = ""
  dependencies = ""
  vars {}
}

