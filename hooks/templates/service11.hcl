{% if is_service %}
terragrunt = {
  terraform {
    source = "{{ source }}"
  }
  include {
    path = "${find_in_parent_folders()}"
  }
  dependencies {
    paths = [{% for i in dependencies %}
    "../{{ i }}"{% endfor %}
    ]
  }
}
{% endif %}
