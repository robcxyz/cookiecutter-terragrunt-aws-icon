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
{% if inputs %}
{% for k, v in inputs.items() %}
{{ k }} = {{ v }}{% endfor %}
{% endif %}