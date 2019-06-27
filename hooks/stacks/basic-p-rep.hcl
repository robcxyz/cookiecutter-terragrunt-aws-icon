ec2 {
  type = "module"
  source = "github.com/{ git_user }/{ repo }.git//{{ module_path }}"
  dependencies = "{ dependencies }"
  vars {
    name = "ec2"
  }
}

security_groups {
  type = "module"
  source = ""
}