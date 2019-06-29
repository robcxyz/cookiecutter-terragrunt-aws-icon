


import hcl
from pprint import pprint

with open('common.hcl', 'r') as f:
    out = hcl.load(f)

pprint(out)