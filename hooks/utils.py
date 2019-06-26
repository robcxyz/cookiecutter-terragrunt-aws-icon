import boto3
import json


def get_availability_zones():
    client = boto3.client('ec2')
    regions =[]
    zones = {}
    for region in client.describe_regions()["Regions"]:
        regions.append(region['RegionName'])
    regions = sorted(regions)
    for region in regions:
        client = boto3.client('ec2', region_name = region)
        zones[region] = []
        for zone in client.describe_availability_zones()['AvailabilityZones']:
            if zone['State'] == 'available':
                zones[region].append(zone['ZoneName'])

    return zones


def write_availability_zones():
    with open('aws_availability_zones.json', 'w') as f:
        json.dump(get_availability_zones(), f)


if __name__ == '__main__':
    write_availability_zones()