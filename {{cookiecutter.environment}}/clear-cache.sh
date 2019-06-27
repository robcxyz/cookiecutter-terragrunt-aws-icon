#!/usr/bin/env bash
for d in icon-dev/*/*/ ; do
    find . -type d -name ".terragrunt-cache" -prune -exec rm -rf {} \;
done
