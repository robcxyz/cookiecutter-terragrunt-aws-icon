# -*- coding: utf-8 -*-
import os
import pytest

from hooks.pre_gen_project import TerragruntGenerator

SINGLE_STACK = {0: {'region': 'ap-northeast-1',
                    'modules': {
                        'vpc': {'type': 'module', 'source': 'github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v1.59.0',
            'dependencies': '', 'vars': {'name': 'vpc-dev', 'enable_nat_gateway': False, 'single_nat_gateway': False,
                                         'enable_dns_hostnames': True, 'enable_dns_support': True}},
    'keys': {'type': 'module', 'source': 'github.com/robcxyz/terragrunt-root-modules.git//common/keys',
             'dependencies': [''], 'vars': {'name': 'keys'}},
    'security_groups': {'type': 'module', 'source': 'github.com/robcxyz/terragrunt-root-modules.git//common/keys',
                        'dependencies': [''], 'vars': {'name': 'security_groups'}},
    'ec2': {'type': 'module', 'source': 'github.com/{ git_user }/{ repo }.git//{{ module_path }}',
            'dependencies': '{ dependencies }', 'vars': {'name': 'ec2'}},
    'ebs': {'type': 'module', 'source': '', 'dependencies': '', 'vars': {}},
    'logging': {'type': 'module', 'source': '', 'dependencies': '', 'vars': {}}}, 'files': {}}}


# def test_render_all(tmpdir):
#
#     p = tmpdir.mkdir("sub")
#     os.chdir(p)
#
#     tg = TerragruntGenerator(debug=True)
#     tg.stack = SINGLE_STACK
#     tg.make_all()



