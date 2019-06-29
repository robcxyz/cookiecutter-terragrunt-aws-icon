{% if is_service %}
terraform {
  source = "{{ source }}"
  extra_arguments "custom_vars" {
    commands  = ["apply", "plan"]
    arguments = ["-var", "foo=42"]
  }
}

include {
  path = find_in_parent_folders()
}
dependencies {
    paths = [{% for i in dependencies %}
    "../{{ i }}"{% endfor %}
}
{% endif %}
inputs = {
  {% for k, v in inputs.items() %}
  {% if v is mapping %}
  {{ k }} = {% for k2, v2 in v.items() %}
    {{ k2 }} = {{ v2 }}
  {% endfor %}
  {% endif %}
  {{ k }} = {{ v }}{% endfor %}
}