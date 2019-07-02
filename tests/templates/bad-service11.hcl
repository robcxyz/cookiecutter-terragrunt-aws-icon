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

{% if inputs %}
{% for k, v in inputs.items() %}{% if v is mapping -%}
{{ k }} = {{ "{" }} {% for k2, v2 in v.items() %}
  {{ k2 }} = "{{ v2 }}"{% endfor %}
{{ "}" }}
{{% elif v is iterable -%}}
{{ k }} = [{% for i in v %}
    "{{ i }}"{% if not loop.last %}","{% endif %}{% endfor %}]
{% else -%}
{{ k }} = "{{ v }}"{% endif %}{% endfor %}
{% endif -%}{% endif %}
