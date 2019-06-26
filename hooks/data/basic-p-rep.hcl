ec2 "basic-single-node" {
  source = "github.com/{ git_user }/{ repo }.git//{{ module_path }}"
  requires = "{{ requires }}"
  dependencies = "{{ dependencies }}"
  vars {
    name = "ec2"
  }
}

security_groups {}