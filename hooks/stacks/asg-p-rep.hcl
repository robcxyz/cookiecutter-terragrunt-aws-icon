asg {
  type = "module"
  source = "github.com/{ git_user }/{ repo }.git//{{ module_path }}"
  dependencies = "{ dependencies }"
  variables {
    name = "ec2"
  }
}

alb {
  type = "module"
  source = ""
  dependencies = ""
  variables {}
}

logging {
  type = "module"
  source = ""
  dependencies = ""
  variables {}
}

