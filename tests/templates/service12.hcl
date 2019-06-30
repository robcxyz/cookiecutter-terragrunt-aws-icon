terraform {
  source = "git::git@github.com:foo/modules.git//frontend-app?ref=v0.0.3"
  extra_arguments "custom_vars" {
    commands  = ["apply", "plan"]
    arguments = ["-var", "foo=42"]
  }
}

include {
  path = find_in_parent_folders()
}
dependencies {
  paths = ["../vpc", "../mysql", "../redis"]
}
inputs = {
  instance_type  = "t2.micro"
  instance_count = 10
}