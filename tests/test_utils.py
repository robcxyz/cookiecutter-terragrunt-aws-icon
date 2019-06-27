# -*- coding: utf-8 -*-
import os
import pytest

from hooks.utils import append_vars_to_tfvars


def test_render_in_place():
    pass

def test_append_vars_to_tfvars(tmpdir):
    tfv = 'example.tfvars'
    p = tmpdir.mkdir("sub").join(tfv)
    append_vars_to_tfvars(p, {'stuff': 'things', 'foo': 'bar'})
    assert p.read() == 'stuff = things\nfoo = bar\n'


