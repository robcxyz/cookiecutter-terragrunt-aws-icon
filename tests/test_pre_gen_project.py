# -*- coding: utf-8 -*-
import os
import pytest

from hooks.pre_gen_project import TerragruntGenerator

def test_ask_simple_question_defaults(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda x: "ben")
    tg = TerragruntGenerator().simple_question('What is your name', 'frank')
    assert tg == "ben"
    tg = TerragruntGenerator().simple_question('What is your name', 'frank')
    assert tg == "frank"


def test_choice_question(monkeypatch):
    pass
