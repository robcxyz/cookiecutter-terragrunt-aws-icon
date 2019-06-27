import os
import json
import boto3
import hcl
from jinja2 import Template, Environment, FileSystemLoader


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

    def get_files(self):
        pass

    def get_modules(self):
        pass

    def main(self):
        self.get_files()
        self.get_modules()
        return self.stack


if __name__ == '__main__':
    pass
