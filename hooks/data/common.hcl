
ec2 "basic-single-node" {
  source = "github.com/{ git_user }/{ repo }.git//{{ module_path }}"
  requires = "{{ requires }}"
  dependencies = "{{ dependencies }}"
  vars {
    name = "vpc-dev"
    enable_nat_gateway = false
    single_nat_gateway = false
    enable_dns_hostnames = true
    enable_dns_support = true
  }
}

security_groups {

}