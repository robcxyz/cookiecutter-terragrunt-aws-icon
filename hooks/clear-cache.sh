#!/usr/bin/env bash

for d in ap-northeast-1/*/*/ ; do
    find . -type d -name ".terragrunt-cache" -prune -exec rm -rf {} \;
done
