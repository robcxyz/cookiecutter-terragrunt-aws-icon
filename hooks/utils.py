import os
import json
import boto3
import hcl
from jinja2 import Template, Environment, FileSystemLoader

from pprint import pprint


def get_availability_zones():
    client = boto3.client('ec2')
    regions = []
    zones = {}
    for region in client.describe_regions()["Regions"]:
        regions.append(region['RegionName'])
    regions = sorted(regions)
    for region in regions:
        client = boto3.client('ec2', region_name=region)
        zones[region] = []
        for zone in client.describe_availability_zones()['AvailabilityZones']:
            if zone['State'] == 'available':
                zones[region].append(zone['ZoneName'])

    return zones


def write_availability_zones():
    with open('aws_availability_zones.json', 'w') as f:
        json.dump(get_availability_zones(), f)


def render_in_place(template_dir, template_name, template_dict):
    env = Environment(loader=FileSystemLoader(template_dir))
    file = env.get_template(template_name)
    return file.render(template_dict)


def append_vars_to_tfvars(tfvars_path, vars_dict):
    with open(tfvars_path, 'a+') as f:
        for k, v in vars_dict.items():
            f.write(f'{k} = {v}\n')


class StackParser(object):
    def __init__(self, hcl_dict):
        self.hcl_dict = hcl_dict
        self.stack = {}

        self.main()

    @staticmethod
    def _validate_format(k, dict):
        required_keys = ['type']
        module_keys = ['dependencies', 'vars', 'source']
        file_keys = ['']

        for key in required_keys:
            if key not in dict.keys():
                raise ValueError(f'Need to set \'{key}\' key for \'{k}\' item')

        if dict['type'] == 'module':
            for key in module_keys:
                if key not in dict.keys():
                    raise ValueError(f'Need to set \'{key}\' key for \'{k}\' item')
        elif dict['type'] == 'file':
            for key in file_keys:
                if key not in dict.keys():
                    raise ValueError(f'Need to set \'{key}\' key for \'{k}\' item')
        else:
            raise ValueError(f'Unrecognized type for \'{k}\' item')

    def main(self):
        self.stack = {'modules': {}, 'files': {}}
        for k, v in self.hcl_dict.items():
            print(v.keys())
            self._validate_format(k, v)
            print(f'processing {k}')
            if v['type'] == 'module':
                # self.stack['modules'][k].update(v)
                self.stack['modules'][k] = v


if __name__ == '__main__':
    with open('stacks/common.hcl', 'rb') as fp:
        out = hcl.loads(fp.read())

    pprint(out.items())
    # for k, v in out.items():
    # print(v)
    pprint(StackParser(out).stack)
    # inp = out['vpc'].keys()
    # print(inp)
    # required_keys = ['type', 'source']
    # optional_keys = ['dependencies', 'vars']
    # for k in required_keys:
    #     if k not in inp
