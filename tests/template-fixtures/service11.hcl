terragrunt = {
  terraform {
    source = "{{ source }}"
  }

  include {
    path = "${find_in_parent_folders()}"
  }

  dependencies {
    paths = [
    ]
  }
}


{% for k, v in vars.items() %}
{{ k }} = {{ v }}
{% endfor %}