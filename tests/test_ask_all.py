# -*- coding: utf-8 -*-
import os
import pytest

from jinja2.exceptions import UndefinedError, TemplateSyntaxError

from hooks.pre_gen_project import TerragruntGenerator

from pprint import pprint


def test_ask_simple_question_defaults(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda x: "ben")
    tg = TerragruntGenerator(debug=True).simple_question('What is your name', 'frank')
    assert tg == "ben"
    monkeypatch.setattr('builtins.input', lambda x: "")
    tg = TerragruntGenerator(debug=True).simple_question('What is your name', 'frank')
    assert tg == "frank"


def test_choice_question(monkeypatch, capsys):
    with pytest.raises(ValueError) as e:
        TerragruntGenerator(debug=True).choice_question('What is your name', 'frank')
    assert "Default is not a list" in str(e.value)

    monkeypatch.setattr('builtins.input', lambda x: "frank")
    tg = TerragruntGenerator(debug=True).choice_question('What is your name', ['frank'])
    assert tg == "frank"

    monkeypatch.setattr('builtins.input', lambda x: "")
    tg = TerragruntGenerator(debug=True).choice_question('What is your name', ['frank', 'sam'])
    assert tg == "frank"

    # TODO: Test for raising "Option not available" -> Possibly related to https://github.com/pytest-dev/pytest/issues/2079


#     See also https://github.com/eisensheng/pytest-catchlog as a possible alternative to capture recursive cli errors


def test_get_aws_availability_zones(monkeypatch, tmpdir):
    monkeypatch.setattr('builtins.input', lambda x: "n")
    tg = TerragruntGenerator(debug=True)
    tg.get_aws_availability_zones()
    assert len(tg.available_azs['ap-northeast-1']) == 3

    # This works but takes 15 seconds...
    # TODO: Put in tmp dir
    # p = tmpdir.mkdir('sub').join('aws_availability_zones.json')
    # monkeypatch.setattr('builtins.input', lambda x: "y")
    # tg = TerragruntGenerator(debug=True)
    # tg.get_aws_availability_zones()
    # assert len(tg.availability_zones['ap-northeast-1']) == 3


# def test_ask_availability_zones(monkeypatch):
#     monkeypatch.setattr('builtins.input', lambda x: "3")
#     tg = TerragruntGenerator(debug=True)
#     tg.ask_availability_zones()
#     assert tg.num_azs == str(3)

# monkeypatch.setattr('builtins.input', lambda x: "max")
# tg = TerragruntGenerator(debug=True, )
# tg.ask_availability_zones()
# assert tg.num_azs == str(3)

# TODO: Test for raising "Option not available"


def test_ask_region(monkeypatch):
    # Single input
    inputs = ['n', 'eu-west-3']
    input_generator = (i for i in inputs)
    monkeypatch.setattr('builtins.input', lambda prompt: next(input_generator))
    tg = TerragruntGenerator(debug=True)
    tg.ask_region()
    pprint(tg.stack)
    assert tg.regions == ['eu-west-3']
    # assert tg.stack == {0: {'region': 'eu-west-3', 'modules': {}}}

    # # Multiple inputs
    # inputs = ['n', 'eu-west-2', 'eu-west-3']
    # input_generator = (i for i in inputs)
    # monkeypatch.setattr('builtins.input', lambda prompt: next(input_generator))
    # tg = TerragruntGenerator(num_regions=2, debug=True)
    # tg.ask_region()
    # assert tg.regions == ['eu-west-2', 'eu-west-3']
    # assert tg.stack == {0: {'region': 'eu-west-2'}, 1: {'region': 'eu-west-3'}}


def test_ask_availability_zones(monkeypatch):
    # Single region
    inputs = ['', 'max']
    input_generator = (i for i in inputs)
    monkeypatch.setattr('builtins.input', lambda prompt: next(input_generator))
    tg = TerragruntGenerator(num_regions=1, debug=True, region='ap-northeast-1')
    tg.get_aws_availability_zones()
    tg.ask_availability_zones()

    assert tg.num_azs == 3


COMMON_FIXTURES = [
    (
        "common.hcl",
        False,
    ),
    (
        "bad-common.hcl",
        True,
    )
]


@pytest.mark.parametrize("hcl_fname,invalid", COMMON_FIXTURES)
def test_ask_common_modules(hcl_fname, invalid, monkeypatch):
    # Single region
    inputs = ['', '']
    input_generator = (i for i in inputs)
    monkeypatch.setattr('builtins.input', lambda prompt: next(input_generator))
    tg = TerragruntGenerator(num_regions=1, debug=True, region='ap-northeast-1',
                             stack={'env_inputs': {}, 0: {'region': 'eu-west-3', 'modules': {}, 'region_inputs': {}}})
    tg.stacks_dir = os.path.join(os.path.abspath(os.path.curdir), 'stacks')
    tg.common_template = hcl_fname
    tg.get_stack_env()
    if not invalid:
        tg.ask_common_modules()
    else:
        with pytest.raises((ValueError, UndefinedError, TemplateSyntaxError)):
            tg.ask_common_modules()

    pprint(tg.stack)
    # assert tg.stack == 3

STACK_FIXTURES = [
    (
        "common.hcl",
        False,
    ),
    (
        "bad-common.hcl",
        True,
    )
]


@pytest.mark.parametrize("hcl_fname,invalid", STACK_FIXTURES)
def test_ask_stack_modules(hcl_fname, invalid, monkeypatch):
    # Single region
    inputs = ['', '']
    input_generator = (i for i in inputs)
    monkeypatch.setattr('builtins.input', lambda prompt: next(input_generator))
    tg = TerragruntGenerator(num_regions=1, debug=True, region='ap-northeast-1',
                             stack={'env_inputs': {}, 0: {'region': 'eu-west-3', 'modules': {}, 'region_inputs': {}}})
    tg.stacks_dir = os.path.join(os.path.abspath(os.path.curdir), 'stacks')
    tg.common_template = hcl_fname
    tg.get_stack_env()
    if not invalid:
        tg.ask_stack_modules()
    else:
        with pytest.raises((ValueError, UndefinedError, TemplateSyntaxError)):
            tg.ask_common_modules()

    pprint(tg.stack)

# def test_ask_all(monkeypatch):
#     # Single regions
#     inputs = ['', '', '']
#     input_generator = (i for i in inputs)
#     monkeypatch.setattr('builtins.input', lambda prompt: next(input_generator))
#     tg = TerragruntGenerator(num_regions=1, debug=True)
#     tg.ask_all()
#     assert tg.stack == {0: {'region': 'ap-northeast-1'}}
#
#     # Single regions
#     inputs = ['', 'ap-northeast-1', 'max']
#     input_generator = (i for i in inputs)
#     monkeypatch.setattr('builtins.input', lambda prompt: next(input_generator))
#     tg = TerragruntGenerator(num_regions=1, debug=True)
#     tg.ask_all()
#     assert tg.num_azs == 3
#
#     # Multiple regions
#     inputs = ['', '', '', 'us-east-2', '']
#     input_generator = (i for i in inputs)
#     monkeypatch.setattr('builtins.input', lambda prompt: next(input_generator))
#     tg = TerragruntGenerator(num_regions=2, debug=True)
#     tg.ask_all()
#     assert tg.stack == {0: {'region': 'ap-northeast-1'}, 1: {'region': 'us-east-2'}}
