#!/usr/bin/env bash
{% for r in regions %}
for d in {{ r }}/*/*/ ; do
    find . -type d -name ".terragrunt-cache" -prune -exec rm -rf {} \;
done
{% endfor %}