# -*- coding: utf-8 -*-
import os
import hcl

import pytest

from pre_gen_project import append_vars_to_tfvars, StackParser


def test_render_in_place():
    pass

def test_append_vars_to_tfvars(tmpdir):
    tfv = 'example.tfvars'
    p = tmpdir.mkdir("sub").join(tfv)
    append_vars_to_tfvars(p, {'stuff': 'things', 'foo': 'bar'})
    assert p.read() == 'stuff = things\nfoo = bar\n'


FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'stack-fixtures')
FIXTURES = [
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

@pytest.mark.parametrize("hcl_fname,invalid", FIXTURES)
def test_stack_parser(hcl_fname, invalid, monkeypatch):
    with open(os.path.join(FIXTURE_DIR, hcl_fname), 'rb') as fp:
        print(f'hcl_fname is {hcl_fname}')
        inp = fp.read()

        if not invalid:
            StackParser(hcl.loads(inp))
        else:
            with pytest.raises(ValueError):
                StackParser(hcl.loads(inp))




