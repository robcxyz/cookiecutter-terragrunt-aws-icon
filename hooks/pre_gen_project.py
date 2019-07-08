from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals
from builtins import str
import os
import json
import logging
import ipaddress
import requests

import shutil

import boto3
import hcl
from jinja2 import Environment, FileSystemLoader

from pprint import pprint

logger = logging.getLogger(__name__)

REGIONS = ['ap-northeast-1', 'ap-northeast-2', 'ap-south-1', 'ap-southeast-1', 'ap-southeast-2', 'ca-central-1',
           'eu-central-1', 'eu-north-1', 'eu-west-1', 'eu-west-2', 'eu-west-3']

RAW_GH = 'https://raw.github.com/robcxyz/cookiecutter-terragrunt-aws-icon/master/'


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


def write_availability_zones(az_path):
    with open(az_path, 'w') as f:
        json.dump(get_availability_zones(), f)


class StackParser(object):
    def __init__(self, hcl_dict):
        self.hcl_dict = hcl_dict
        self.stack = {}
        self.required_keys = {}
        self.module_keys = {
            'source': {'type': str, 'optional': False, 'target': 'modules'},
            'dependencies': {'type': list, 'optional': True, 'target': 'modules'},
            'inputs': {'type': dict, 'optional': True, 'target': 'modules'},
            'env_inputs': {'type': dict, 'optional': True, 'target': 'env_inputs'},
            'region_inputs': {'type': dict, 'optional': True, 'target': 'region_inputs'},
        }
        self.file_keys = {}

        self.stack = {'modules': {}, 'files': {}, 'env_inputs': {}, 'region_inputs': {}}
        self.main()

    def _validate_format(self, k, stack_dict):
        # {% raw %}
        # {% endraw %}
        for key in self.required_keys.items():
            if key not in stack_dict.keys():
                error_msg = 'Need to set \'%s\' key for \'%s\' item' % (key, k)
                print(error_msg)
                raise ValueError(error_msg)

        # if dict['type'] == 'module':
        for key, val in self.module_keys.items():
            if not val['optional']:
                if key not in stack_dict.keys():
                    error_msg = 'Need to set \'%s\' key for \'%s\' item' % (key, k)
                    print(error_msg)
                    raise ValueError(error_msg)
                if not isinstance(stack_dict[key], val['type']):
                    # print('stack_dict = %s %s') % (str(stack_dict[key]), str(val['type']))
                    error_msg = '%s needs to be of type %s for \'%s\' item' % (key, str(val['type']), k)
                    print(error_msg)
                    raise ValueError(error_msg)
            if val['optional']:
                if key in stack_dict.keys():
                    if not isinstance(stack_dict[key], val['type']):
                        # print('stack_dict = %s %s') % (str(stack_dict[key]), str(val['type']))
                        error_msg = '%s needs to be of type %s for \'%s\' item' % (key, str(val['type']), k)
                        print(error_msg)
                        raise ValueError(error_msg)

    def main(self):

        for k, v in self.hcl_dict.items():
            self._validate_format(k, v)
            if v['type'] == 'module':
                # self.stack['modules'][k].update(v)
                self.stack['modules'].update({k: {'source': v['source']}})
                for i in [opt for opt in self.module_keys.items() if opt[1]['optional']]:
                    if i[0] in v.keys() and i[1]['target'] == 'modules':
                        self.stack['modules'][k].update({i[0]: v[i[0]]})
                    elif i[0] in v.keys() and i[1]['target'] != 'modules':
                        self.stack[i[1]['target']].update(v[i[0]])

        return self.stack


class TerragruntGenerator(object):

    def __init__(self, environment='dev', num_regions=1, debug=False, headless=False, *args, **kwargs):
        self.debug = debug
        self.terraform_version = None
        self.terragrunt_file = None
        self.headless = headless

        if not self.debug:
            os.mkdir(os.path.join(os.path.curdir, 'hooks'))  # Initialize the hooks directory
            os.mkdir(os.path.join(os.path.curdir, 'hooks', 'stacks'))
            os.mkdir(os.path.join(os.path.curdir, 'hooks', 'templates'))

        if self.debug:
            self.stacks_dir = os.path.join(os.path.abspath(os.path.curdir), '..', 'tests',  'stacks')
            self.templates_dir = os.path.join(os.path.abspath(os.path.curdir), '..', 'tests',  'templates')
        else:
            self.stacks_dir = os.path.join(os.path.curdir, 'hooks', 'stacks')
            self.templates_dir = os.path.join(os.path.curdir, 'hooks', 'templates')

        if not self.debug:
            self.get_all_templates()

        # These values need override to pass tests instead of rendering them
        if self.debug:
            self.environment = environment
            self.num_regions = num_regions
            self.cidr = '10.0.0.0/16'
        else:
            self.environment = '{{ cookiecutter.environment }}'
            self.num_regions = int('{{ cookiecutter.num_regions }}')
            self.cidr = ('{{ cookiecutter.cidr }}')
        self.r = 0  # Region counter

        self.got_az_list = False
        self.rebuild_availability_zones = None
        self.region = None
        self.regions = []
        self.region_num = None
        self.possible_regions = None
        self.num_azs = None
        self.ha = False
        self.availability_zones = None

        self.stack = {'env_inputs': {}}
        self.use_common_modules = None
        self.available_azs = None

        self.num_vpcs = 1
        self.num_subnets = 2
        self.subnet_names = None

        self.cidr_netmask = None
        self.possible_subnets = None
        self.subnets = None

        self.common_modules = {}
        self.common_template = 'common.hcl'
        self.common_dict = {}

        self.use_stack_modules = None
        self.stack_names = []
        self.stack_type = None
        self.stack_modules = {}
        self.stack_template = None

        self.use_special_modules = None
        self.special_modules_location = None

        self.forked_repo = 'n'
        self.already_forked = False
        self.git_user = 'robcxyz'
        self.repo = 'terragrunt-modules-'

        self.tpl_env = None
        self.stack_env = None
        self.service_template = None
        self.head_template = None

        for d in args:
            for key in d:
                setattr(self, key, d[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def region_init(self):
        pass

    @staticmethod
    def simple_question(question, default=None):
        prompt = '%s:' % (question)
        if default:
            # prompt = f'{question}-\n[{default}]:'
            prompt = '%s-\n%s:' % (question, default.encode("utf-8"))
        try:
            user_entry = input(prompt)
        except SyntaxError:
            user_entry = None
        if not user_entry and default is not None:
            user_entry = default
        if not user_entry and default is None:
            raise ValueError
        return user_entry

    @staticmethod
    def choice_question(question, defaults):
        """returns error when not in choices"""
        if not isinstance(defaults, list):
            raise ValueError("Default is not a list")
        choices = frozenset(defaults)
        input_question = '%s-\n%s:' % (question, [str(r) for r in defaults])

        tries = 0
        try:
            while True:
                user_entry = input(input_question)
                if user_entry in choices:
                    break
                elif user_entry == "":
                    break
                elif tries > 5:
                    raise ValueError('Too many attempts - exiting')
                else:
                    print("Option not available")
                    tries += 1
        except SyntaxError:
            user_entry = None
        if not user_entry:
            user_entry = defaults[0]
        return user_entry

    @staticmethod
    def get_and_write_raw_content(path):
        if isinstance(path, list):
            r = requests.get(RAW_GH + '/'.join(path)).text
            with open(os.path.join(os.path.curdir, '/'.join(path)), 'w') as f:
                f.write(r)
        elif isinstance(path, str):
            r = requests.get(RAW_GH + path).text
            with open(os.path.join(os.path.curdir, path), 'w') as f:
                f.write(r)

    def get_all_templates(self):
        template_list = ['clear-cache.sh.tpl', 'head11.hcl', 'head12.hcl', 'service11.hcl', 'service12.hcl']
        for t in template_list:
            self.get_and_write_raw_content(['hooks', 'templates', t])

    def get_aws_availability_zones(self):
        az_list_path = os.path.join(os.path.curdir, 'hooks', 'aws_availability_zones.json')
        if not self.got_az_list:
            self.rebuild_availability_zones = self.choice_question(
                'Would you like to update the availabilty zones list?',
                ['n', 'y'])
            if self.rebuild_availability_zones == 'y':
                write_availability_zones(az_list_path)
            else:
                r = requests.get(RAW_GH + '/hooks/aws_availability_zones.json').text
                with open(az_list_path, 'w') as f:
                    f.write(r)

            with open(os.path.join(os.path.curdir, 'hooks', 'aws_availability_zones.json'), 'r') as f:
                self.available_azs = json.load(f)

                self.possible_regions = list(self.available_azs.keys())
                self.got_az_list = True

    def ask_region(self):
        self.get_aws_availability_zones()
        region = self.choice_question('Enter region number %d to deploy into? \n' % (self.r + 1),
                                      list(self.possible_regions))
        if region in self.regions:
            raise ValueError('Entered duplicate regions - exiting')
        self.regions.append(region)
        self.possible_regions.remove(region)
        self.region = region

    def ask_availability_zones(self):
        self.num_azs = self.choice_question('How many availability zones?',
                                            [1, 2, 3, 4, 5, 6, 7, 'max'])
        # Validate
        if self.num_azs != 'max':
            if int(self.num_azs) > len(self.available_azs[self.region]):
                raise ValueError('Entered too many availability zones')
        if self.num_azs != 1:
            self.ha = True
        # Set
        if self.num_azs == 'max':
            self.num_azs = len(self.available_azs[self.region])
            self.availability_zones = self.available_azs[self.region]
        else:
            self.num_azs = int(self.num_azs)
            self.availability_zones = self.available_azs[self.region][0:self.num_azs]

    def build_network(self):
        self.cidr_netmask = int(self.cidr.split('/')[1])

        self.possible_subnets = list(ipaddress.ip_network(self.cidr).subnets(
            prefixlen_diff=(self.netmask - self.cidr_netmask)))
        self.subnets = self.possible_subnets[0:(self.num_subnets * self.num_azs)]

    def ask_networking(self):
        # TODO: Get rid of this?
        self.num_vpcs = self.choice_question('How many vpcs?', [1, 2, 3, 4])
        self.num_subnets = int(self.choice_question('How many subnets?', [2, 3, 4, 5]))
        self.subnet_names = ['private_subnets', 'public_subnets', 'database_subnets',
                             'elasticache_subnets', 'redshift_subnets', 'infra_subnets'][0:self.num_subnets]
        self.netmask = int(self.choice_question('What size netmask?', [20, 22, 24]))

        self.build_network()

    def module_ask_module_location(self):
        # TODO:
        if self.use_common_modules == 'y' and not self.already_forked:
            self.forked_repo = self.choice_question('Do you have a private fork? \n '
                                                    '(I\'d fork it if you want to customize it .)', ['n', 'y'])

    def module_ask_git_user(self):
        # TODO:
        if self.forked_repo == 'y' and not self.already_forked:
            self.git_user = self.simple_question('What is your github username / organization?', ['y', 'n'])
            self.already_forked = True

    def module_ask_all(self):
        """TODO: This is premature."""
        self.module_ask_module_location()
        self.module_ask_git_user()

    def ask_common_modules(self):
        self.use_common_modules = self.choice_question('Would you like to use common modules', ['y', 'n'])
        if self.use_common_modules == 'y':
            try:
                self.get_and_write_raw_content(['hooks', 'stacks', 'common.hcl'])

                common_str = self.stack_env.get_template(self.common_template).render(self.common_dict)
                self.common_modules = hcl.loads(common_str)
                parsed_stack = StackParser(self.common_modules).stack
                self.stack[self.r]['modules'].update(parsed_stack['modules'])
                self.stack[self.r]['region_inputs'].update(parsed_stack['region_inputs'])
                self.stack['env_inputs'].update(parsed_stack['env_inputs'])
            except:
                err_msg = 'Could not read common modules, invalid format'
                print(err_msg)
                raise ValueError(err_msg)

    def ask_stack_modules(self):

        self.use_stack_modules = self.choice_question('Do you want to use a generic stack?\n', ['y', 'n'])
        if self.use_stack_modules == 'y':
            # stack_options = os.listdir(self.stacks_dir).remove('common.hcl')  # This won't work for testing but
            # something like it should be built to qualify a list of possible stacks
            stack_options = ['basic-p-rep', 'decoupled-p-rep', 'data-science', 'data-engineering-hadoop']
            self.stack_type = self.choice_question('What type of stack are you building?\n', stack_options)
            # TODO: Perhaps qualify the options first or allow for alternative input
            self.stack_template = str(self.stack_type) + '.hcl'

            self.get_and_write_raw_content(['hooks', 'stacks', self.stack_template])

            stack_str = self.stack_env.get_template(self.stack_template).render(self.common_dict)
            try:
                self.common_modules = hcl.loads(stack_str)
                parsed_stack = StackParser(self.common_modules).stack
                self.stack[self.r]['modules'].update(parsed_stack['modules'])
                self.stack[self.r]['region_inputs'].update(parsed_stack['region_inputs'])
                self.stack['env_inputs'].update(parsed_stack['env_inputs'])
            except:
                err_msg = 'Could not read stack modules, invalid format'
                print(err_msg)
                raise ValueError(err_msg)

    def ask_special_modules(self):

        self.use_special_modules = self.choice_question('Would you like to enter any special modules?', ['n', 'y'])

        if self.use_special_modules == 'y':
            self.special_modules_location = self.choice_question('Where would you like to import special modules from?',
                                                                 ['local', 'github', 'url'])
            # TODO: This should iterate until the user stops entering information.  This is also pretty dumb as the user
            # at that point can just copy and paste so not sure what the purpose of this really is
            # The real value in this tool is just to have a simple cli to get users into the ecosystem
            # Many users will not even need to have customizations as they'll be working on another layer (ie application)
            if self.special_modules_location == 'local':
                pass
            if self.special_modules_location == 'github':
                pass
            if self.special_modules_location == 'url':
                pass

    def ask_terragrunt_version(self):
        if not self.headless:
            self.terraform_version = self.choice_question('What version of Terraform do you want to use?',
                                                          ['0.11', '0.12'])
        if self.terraform_version == '0.11':
            self.terraform_version = str(11)
            self.terragrunt_file = 'terraform.tfvars'
        else:
            self.terraform_version = str(12)
            self.terragrunt_file = 'terragrunt.hcl'

        # if not self.debug:
        self.service_template = 'service' + str(self.terraform_version) + '.hcl'
        self.head_template = 'head' + str(self.terraform_version) + '.hcl'

    def ask_all(self):
        for r in range(self.num_regions):
            self.get_stack_env()
            self.r = r
            self.ask_region()
            self.stack[self.r] = {'region': self.region, 'modules': {}, 'region_inputs': {},
                                  'files': {}}

            # TODO: Encapsulate logic in separate coockiecutter for AZs and networking
            # self.ask_availability_zones()
            # self.stack[self.r]['azs'] = self.availability_zones
            # self.common_dict = {'avs': self.availability_zones}
            # self.ask_networking()
            self.ask_common_modules()
            self.ask_stack_modules()
            self.ask_special_modules()
            self.ask_terragrunt_version()

    def make_azs(self):
        pass

    def make_modules(self):
        for r in range(self.num_regions):
            self.region_num = r
            region_modules = self.stack[r]['modules'].keys()

            for m in region_modules:
                # module_path = os.path.join(os.path.abspath(os.path.curdir), self.stack[r]['region'], m)
                module_path = os.path.join(os.path.curdir, self.stack[r]['region'], m)
                os.makedirs(module_path)
                stack_dict = self.stack[r]['modules'][m]

                stack_dict.update({'is_service': True})  # TODO: This needs to be pulled out in the headless...

                env_tpl = self.tpl_env.get_template(self.service_template)
                rendered_file = env_tpl.render(stack_dict)
                with open(os.path.join(module_path, self.terragrunt_file), 'w+') as fp:
                    fp.write(rendered_file)
            self.make_region()

    def make_region(self):
        region_path = os.path.join(os.path.abspath(os.path.curdir), self.stack[self.region_num]['region'])
        self.stack[self.r]['region_inputs'].update({'region': self.region})
        region_dict = {'is_service': False, 'inputs': self.stack[self.r]['region_inputs']}
        rendered_file = self.tpl_env.get_template(self.service_template).render(region_dict)
        with open(os.path.join(region_path, 'region.tfvars'), 'w') as fp:
            fp.write(rendered_file)

    def make_env(self):
        env_dict = {'is_service': False,
                    'inputs': {'environment': '{{ cookiecutter.environment }}',
                               'tags': {'Environment': '{{ cookiecutter.environment }}'}}}
        env_dict['inputs'].update(self.stack['env_inputs'])
        rendered_file = self.tpl_env.get_template(self.service_template).render(env_dict)
        with open(os.path.join(os.path.curdir, 'environment.tfvars'), 'w') as fp:
            fp.write(rendered_file)

    def make_head(self):
        env_dict = {}  # Don't know of any rendering here
        rendered_file = self.tpl_env.get_template(self.head_template).render(env_dict)
        with open(os.path.join(os.path.curdir, self.terragrunt_file), 'w') as fp:
            fp.write(rendered_file)

    def make_other(self):
        rendered_file = self.tpl_env.get_template('clear-cache.sh.tpl').render(regions=self.regions)
        with open(os.path.join(os.path.curdir, 'clear-cache.sh'), 'w') as fp:
            fp.write(rendered_file)

    def get_tpl_env(self):
        self.tpl_env = Environment(loader=FileSystemLoader(self.templates_dir))  # Separate for testing purposes

    def get_stack_env(self):
        # TODO: This is perhaps where you would want to put in functionality to do custom imports
        self.stack_env = Environment(loader=FileSystemLoader(self.stacks_dir))  # Separate for testing purposes

    def make_all(self):
        self.get_tpl_env()
        # Make the path first
        self.make_modules()  # self.make_region() inside
        self.make_env()
        self.make_head()
        self.make_other()
        with open('stack.json', 'w') as fp:
            json.dump(self.stack, fp)

    # def rm_hooks(self):
    #     os.rmdir(os.path.join(os.path.curdir))

    def main(self):
        if not self.headless:
            self.ask_all()
        self.make_all()



if __name__ == '__main__':
    tg = TerragruntGenerator(debug=False)
    tg.main()
