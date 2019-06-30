# -*- coding: utf-8 -*-
import os
import pytest
import hcl

from hooks.pre_gen_project import TerragruntGenerator, StackParser

from jinja2.exceptions import UndefinedError

from tests.test_render_all import FIXTURE_DIR as RENDER_FIXTURE_DIR

SINGLE_STACK = {0: {'region': 'ap-northeast-1',
                    'modules': {
                        'vpc': {'type': 'module',
                                'source': 'github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v1.59.0',
                                'dependencies': '',
                                'vars': {'name': 'vpc-dev', 'enable_nat_gateway': False, 'single_nat_gateway': False,
                                         'enable_dns_hostnames': True, 'enable_dns_support': True}},
                        'keys': {'type': 'module',
                                 'source': 'github.com/robcxyz/terragrunt-root-modules.git//common/keys',
                                 'dependencies': [''], 'vars': {'name': 'keys'}},
                        'security_groups': {'type': 'module',
                                            'source': 'github.com/robcxyz/terragrunt-root-modules.git//common/keys',
                                            'dependencies': [''], 'vars': {'name': 'security_groups'}},
                        'ec2': {'type': 'module', 'source': 'github.com/{ git_user }/{ repo }.git//{{ module_path }}',
                                'dependencies': '{ dependencies }', 'vars': {'name': 'ec2'}},
                        'ebs': {'type': 'module', 'source': '', 'dependencies': '', 'vars': {}},
                        'logging': {'type': 'module', 'source': '', 'dependencies': '', 'vars': {}}}, 'files': {}}}

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'stacks')
STACK_FIXTURES = [
    (
        "common.hcl",
        False,
    ),
    (
        "basic-p-rep.hcl",
        False,
    ),
    (
        "bad-hcl.hcl",
        True,
    ),
    (
        "bad-common.hcl",
        True,
    )
]
HEAD_FIXTURES = [
    (
        "head",
        False
    ),
    # (
    #     "bad-head",
    #     True,
    # )
]

SERVICE_FIXTURES = [
    (
        "service",
        False
    ),
    # (
    #     "bad-service",
    #     True,
    # )
]

# TODO: RM all this once 11 is completely gone
VERSION_FIXTURES = [
    (
        "0.11",
    ),
    (
        "0.12",
    )
]


@pytest.mark.parametrize("hcl_fname,invalid", STACK_FIXTURES)
def test_stack_parser(hcl_fname, invalid):
    with open(os.path.join(FIXTURE_DIR, hcl_fname), 'rb') as fp:
        print(f'hcl_fname is {hcl_fname}')
        inp = fp.read()

        if not invalid:
            StackParser(hcl.loads(inp))
        else:
            with pytest.raises(ValueError):
                StackParser(hcl.loads(inp))


@pytest.mark.parametrize("stack_file,stack_invalid", STACK_FIXTURES)
@pytest.mark.parametrize("service_file,service_invalid", SERVICE_FIXTURES)
@pytest.mark.parametrize("head_file,head_invalid", HEAD_FIXTURES)
@pytest.mark.parametrize("version", VERSION_FIXTURES)
def test_make_all(stack_file, stack_invalid, service_file, service_invalid, head_file, head_invalid, version,
                  tmpdir, monkeypatch):
    # inputs = ['']
    # input_generator = (i for i in inputs)
    # monkeypatch.setattr('builtins.input', lambda prompt: next(input_generator))

    tg = TerragruntGenerator(debug=True, terraform_version=version, headless=True)
    tg.templates_dir = RENDER_FIXTURE_DIR
    tg.stacks_dir = FIXTURE_DIR

    tg.ask_terragrunt_version()

    tg.head_template = head_file + tg.terraform_version + '.hcl'
    tg.service_template = service_file + tg.terraform_version + '.hcl'
    print('\n\n\nhere')
    print(tg.head_template)
    print(tg.service_template)
    p = tmpdir.mkdir("sub")
    os.chdir(p)

    print()

    with open(os.path.join(FIXTURE_DIR, stack_file), 'r') as fp:
        print(f'\n\ntpl_fname is {service_file}\n\n')
        if not stack_invalid:
            print(f'f{stack_file} stack is valid')
            inp = hcl.load(fp)
            tg.stack[0] = StackParser(inp).stack
            tg.stack[0].update({'region': 'ap-northeast-1'})

            if not service_invalid and not head_invalid:
                print('Valid \n\n\n')
                tg.make_all()
            else:
                # with pytest.raises((ValueError, UndefinedError)):
                with pytest.raises(ValueError):
                    print('Invalid \n\n\n')
                    tg.make_all()
        else:
            with pytest.raises((ValueError, KeyError)):
                tg.make_all()

    # assert os.listdir(p) == ['ap-northeast-1']
