

import json
from pprint import pprint

with open('aws_availability_zones.json', 'r') as f:
    out = json.load(f)

# pprint(out)

pprint(out['us-east-1'][0:1])