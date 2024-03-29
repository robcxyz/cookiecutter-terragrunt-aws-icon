{% if is_service %}
terragrunt = {
  terraform {
    source = "{{ source }}"
  }
  include {
    path = "${find_in_parent_folders()}"
  }
{% if dependencies %}
  dependencies {
    paths = [{% for i in dependencies %}
    "../{{ i }}"{% if not loop.last %}","{% endif %}{% endfor %}
    ]
  }{% endif %}
}
{% endif %}
{% if inputs %}inputs = {
  {% for k, v in inputs.items() %}{% if v is mapping %}
  {{ k }} = {{ "{" }} {% for k2, v2 in v.items() %}
    {{ k2 }} = "{{ v2 }}"{% endfor %}
  {{ "}" }}
{% else %}
  {{ k }} = "{{ v }}"{% endif %}{% endfor %}
}{% endif %}
