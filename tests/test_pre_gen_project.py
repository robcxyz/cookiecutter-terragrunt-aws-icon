# -*- coding: utf-8 -*-
import os
import pytest

from hooks.pre_gen_project import TerragruntGenerator

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

    # monkeypatch.setattr('builtins.input', lambda x: "")
    # tg = TerragruntGenerator(debug=True).choice_question('What is your name', ['frank', 'bill'])
    # assert tg == "frank"

    # TODO: Test for raising "Option not available" -> Possibly related to https://github.com/pytest-dev/pytest/issues/2079
#     See also https://github.com/eisensheng/pytest-catchlog as a possible alternative to capture recursive cli errors


def test_get_aws_availability_zones(monkeypatch):

    monkeypatch.setattr('builtins.input', lambda x: "n")
    tg = TerragruntGenerator(debug=True)
    tg.get_aws_availability_zones()
    assert len(tg.availability_zones['ap-northeast-1']) == 3

    # This works but takes 15 seconds...
    # monkeypatch.setattr('builtins.input', lambda x: "y")
    # tg = TerragruntGenerator(debug=True)
    # tg.get_aws_availability_zones()
    # assert len(tg.availability_zones['ap-northeast-1']) == 3


def test_ask_availability_zones(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda x: "3")
    tg = TerragruntGenerator(debug=True)
    tg.ask_availability_zones()
    assert tg.num_azs == str(3)

    # monkeypatch.setattr('builtins.input', lambda x: "max")
    # tg = TerragruntGenerator(debug=True, )
    # tg.ask_availability_zones()
    # assert tg.num_azs == str(3)

    # TODO: Test for raising "Option not available"
