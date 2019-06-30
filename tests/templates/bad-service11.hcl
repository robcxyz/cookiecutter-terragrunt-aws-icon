terragrunt = {
  terraform {
    source = "{{ source }}"
  }

  include {
    path = "${find_in_parent_folders()}"
  }

  dependencies {
    paths = [
      {% for i in dependencies %}
    "../{{ i }}{% endfor %}" {% endfor %}
    ]
  }
}

resource_group = "{{ resource_group }}"


{% for k, v in inputs.items() %}
//{% if v is mapping %}
//{{ k }} = {% for k2, v2 in v.items() %}
//  {{ k2 }} = {{ v2 }}
{% endfor %}
//{% endif %}
{{ k }} = {{ v }}{% endfor %}
{% endfor %}

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
{% if inputs %}
{% for k, v in inputs.items() %}
{{ k }} = {{ v }}{% endfor %}
{% endif %}
