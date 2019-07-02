# -*- coding: utf-8 -*-
import os
import pytest
import hcl

from jinja2.exceptions import UndefinedError

from hooks.pre_gen_project import TerragruntGenerator, StackParser

SINGLE_STACK = {'env_inputs': {},
                0: {'region': 'ap-northeast-1',
                    'region_inputs': {'cidr': '{{ cookiecutter.cidr }}'},
                    'env_inputs': {},
                    'modules': {
                        'vpc': {'type': 'module',
                                'source': 'github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v1.59.0',
                                'dependencies': [''],
                                'inputs': {'name': 'vpc-dev', 'enable_nat_gateway': False, 'single_nat_gateway': False,
                                           'enable_dns_hostnames': True, 'enable_dns_support': True}},
                        'keys': {'type': 'module',
                                 'source': 'github.com/robcxyz/terragrunt-root-modules.git//common/keys',
                                 'dependencies': [''],
                                 'inputs': {'name': 'keys'}},
                        'security_groups': {'type': 'module',
                                            'source': 'github.com/robcxyz/terragrunt-root-modules.git//common/keys',
                                            'dependencies': [''],
                                            'inputs': {'name': 'security_groups'}},
                        'ec2': {'type': 'module',
                                'source': 'github.com/{ git_user }/{ repo }.git//{{ module_path }}',
                                'dependencies': ['{ dependencies }'],
                                'inputs': {'name': 'ec2'}},
                        'ebs': {'type': 'module',
                                'source': '',
                                'dependencies': [''],
                                'inputs': {}},
                        'logging': {'type': 'module',
                                    'source': '',
                                    'dependencies': [''],
                                    'inputs': {}}},
                    'files': {}}}

VPC_MODULE = SINGLE_STACK[0]['modules']['vpc']

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

FIXTURES = [
    (
        "head11.hcl",
        False,
        "0.11",

    ),
    (
        "head12.hcl",
        False,
        "0.12"
    ),
    (
        "service11.hcl",
        False,
        "0.11"
    ),
    (
        "service12.hcl",
        False,
        "0.12"
    ),
    (
        "bad-head11.hcl",
        True,
        "0.11"
    ),
    (
        "bad-head12.hcl",
        True,
        "0.12"
    ),
    (
        "bad-service11.hcl",
        True,
        "0.11"
    ),
    (
        "bad-service12.hcl",
        True,
        "0.12"
    ),
]


@pytest.mark.parametrize("tpl_fname,invalid,version", FIXTURES)
def test_render_service_vpc(tpl_fname, invalid, version, tmpdir):
    with open(os.path.join(FIXTURE_DIR, tpl_fname), 'rb') as fp:
        print(f'\n\ntpl_fname is {tpl_fname}\n\n')

        if not invalid:
            inp = fp.read()
            tg = TerragruntGenerator(debug=True, terraform_version=version, headless=True)
            tg.templates_dir = FIXTURE_DIR
            tg.stack = SINGLE_STACK
            tg.ask_terragrunt_version()

            p = tmpdir.mkdir("sub")
            os.chdir(p)

            tg.make_all()
            # print(os.listdir("ap-northeast-1/ebs"))

        else:
            with pytest.raises((ValueError, UndefinedError)):
                hcl.loads(fp.read())
