# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import os
import pytest

from hooks.pre_gen_project import TerragruntGenerator

from pprint import pprint

NETWORKS = [
    (
        3,
        '10.0.0.0/16',
        20,
        6,
        ['10.0.0.0/20', '10.0.16.0/20', '10.0.32.0/20']
    ),
    (
        1,
        '10.0.0.0/16',
        24,
        9,
        ['10.0.0.0/20', '10.0.16.0/20', '10.0.32.0/20']
    )
]


@pytest.mark.parametrize("azs,cidr,mask,num_subnets,result", NETWORKS)
def test_ask_networking(azs, cidr, mask, num_subnets, result,
                        monkeypatch, tmpdir):
    inputs = ['', '', '']
    input_generator = (i for i in inputs)
    monkeypatch.setattr('builtins.input', lambda prompt: next(input_generator))

    p = tmpdir.mkdir("sub")
    os.chdir(p)

    tg = TerragruntGenerator(debug=True, terraform_version="0.11", headless=True, num_azs=3)
    tg.ask_terragrunt_version()

    tg.num_vpcs = 1
    tg.num_subnets = num_subnets
    tg.subnet_names = ['private_subnets', 'public_subnets', 'database_subnets',
                             'elasticache_subnets', 'redshift_subnets', 'infra_subnets'][0:num_subnets]
    tg.num_azs = azs

    tg.netmask = mask

    tg.build_network()
    print('\n')
    pprint(str(tg.subnets[0]))

    print('\n')
    pprint(str(tg.subnets))

    # pprint(type(tg.subnets))

