
terraform {
  source = "git::git@github.com:foo/modules.git//frontend-app?ref=v0.0.3"
  extra_arguments "custom_vars" {
    commands = [
      get_terraform_commands_that_need_locking(),
      get_terraform_commands_that_need_vars()]
    arguments = [
      "-var",
      "foo=42"]
    required_var_files = [
      "${get_parent_tfvars_dir()}/${path_relative_to_include()}/${find_in_parent_folders(region.tfvars)}",
      "${get_parent_tfvars_dir()}/${path_relative_to_include()}/${find_in_parent_folders(environment.tfvars)}",
      "${get_parent_tfvars_dir()}/${path_relative_to_include()}/${find_in_parent_folders(account.tfvars)}"
    ]
  }
}

extra_arguments "disable_input" {
  commands = [
    "${get_terraform_commands_that_need_input()}"]
  arguments = [
    "-input=false"]
}

after_hook "copy_common_main_variables" {
  commands = [
    "init-from-module"]
  execute = [
    "cp",
    "${get_parent_tfvars_dir()}/common/common_variables.tf",
    "."]
}

after_hook "copy_common_main_providers" {
  commands = [
    "init-from-module"]
  execute = [
    "cp",
    "${get_parent_tfvars_dir()}/common/common_providers.tf",
    "."]
}

remote_state {
  backend = "s3"
  config = {
    bucket = "terraform-states-" + get_aws_account_id()
    encrypt = true
    region = "us-east-1"
    key = "${path_relative_to_include()}/terraform.tfstate"
    bucket = "terraform-states-${get_aws_account_id()}"
    dynamodb_table = "terraform-locks-${get_aws_account_id()}"

    skip_requesting_account_id = "true"
    skip_get_ec2_platforms = "true"
    skip_metadata_api_check = "true"
    skip_region_validation = "true"
    skip_credentials_validation = "true"

    s3_bucket_tags = {
      owner = "{{ owner }}"
      owner_email = "{{ owner_email }}"
      name = "{{ "
    }

    dynamodb_table_tags = {
      owner = "{{  }}"
      name = ""
    }
  }
}

