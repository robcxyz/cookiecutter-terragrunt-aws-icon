terraform {
  source = "git::git@github.com:foo/modules.git//frontend-app?ref=v0.0.3"
  extra_arguments "custom_vars" {
    commands  = [get_terraform_commands_that_need_locking(), get_terraform_commands_that_need_vars()]
    arguments = ["-var", "foo=42"]
    required_var_files = [
        "${get_parent_tfvars_dir()}/${path_relative_to_include()}/${find_in_parent_folders(region.tfvars)}",
        "${get_parent_tfvars_dir()}/${path_relative_to_include()}/${find_in_parent_folders(environment.tfvars)}",
        "${get_parent_tfvars_dir()}/${path_relative_to_include()}/${find_in_parent_folders(account.tfvars)}"
      ]
  }
}

remote_state {
  backend = "s3"
  config = {
    bucket = "terraform-states-" + get_aws_account_id()

    s3_bucket_tags = {
      owner = "terragrunt integration test"
      name = "Terraform state storage"
    }

    dynamodb_table_tags = {
      owner = "terragrunt integration test"
      name = "Terraform lock table"
    }
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