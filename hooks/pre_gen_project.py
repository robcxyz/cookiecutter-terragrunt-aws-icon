import os
import json
import shutil

import boto3
import hcl
from jinja2 import Environment, FileSystemLoader

REGIONS = ['ap-northeast-1', 'ap-northeast-2', 'ap-south-1', 'ap-southeast-1', 'ap-southeast-2', 'ca-central-1',
           'eu-central-1', 'eu-north-1', 'eu-west-1', 'eu-west-2', 'eu-west-3']


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


class StackParser(object):
    def __init__(self, hcl_dict):
        self.hcl_dict = hcl_dict
        self.stack = {}

        self.main()

    @staticmethod
    def _validate_format(k, stack_dict):
        required_keys = {}
        module_keys = {'dependencies': {'type': list},
                       'inputs': {'type': dict},
                       'source': {'type': str}}
        file_keys = ['']

        for key in required_keys.items():
            if key not in stack_dict.keys():
                error_msg = 'Need to set \'%s\' key for \'%s\' item' % (key, k)
                raise ValueError(error_msg)

        # if dict['type'] == 'module':
        for key, val in module_keys.items():
            if key not in stack_dict.keys():
                error_msg = 'Need to set \'%s\' key for \'%s\' item' % (key, k)
                raise ValueError(error_msg)
            if not isinstance(stack_dict[key], val['type']):
                error_msg = '%s needs to be of type %s for \'%s\' item' % (key, str(val['type']), k)
                raise ValueError(error_msg)

        # TODO: RM for files?  Need to update 'type' condition...
        # if dict['type'] == 'file':
        # for key in file_keys:
        #         if key not in dict.keys():
        #             error_msg = 'Need to set \'%s\' key for \'%s\' item' % (key, k)
        #             raise ValueError(error_msg)
        # else:
        #     error_msg = 'Unrecognized type for \'%s\' item' % (k)
        #     raise ValueError(error_msg)

    def main(self):
        self.stack = {'modules': {}, 'files': {}}
        for k, v in self.hcl_dict.items():
            self._validate_format(k, v)
            if v['type'] == 'module':
                # self.stack['modules'][k].update(v)
                self.stack['modules'][k] = v
        return self.stack


class TerragruntGenerator(object):

    def __init__(self, environment='dev', num_regions=1, debug=False, headless=False, *args, **kwargs):
        self.debug = debug
        self.terraform_version = None
        self.terragrunt_file = None
        self.headless = headless
        self.stacks_dir = os.path.join(os.path.abspath(os.path.curdir), '..', 'hooks', 'stacks')
        self.templates_dir = os.path.join(os.path.abspath(os.path.curdir), '..', 'hooks', 'templates')

        # These values need override to pass tests instead of rendering them
        if self.debug:
            self.environment = environment
            self.num_regions = num_regions

        else:
            self.environment = '{{ cookiecutter.environment }}'
            self.num_regions = int('{{ cookiecutter.num_regions }}')
        self.r = 0  # Region counter

        if self.num_regions > 1:
            self.ha = True
        else:
            self.ha = False

        self.got_az_list = False
        self.rebuild_availability_zones = None
        self.region = None
        self.regions = []
        self.possible_regions = None
        self.num_azs = None

        self.stack = {}
        self.use_common_modules = None
        self.availability_zones = None

        self.common_modules = {}

        self.use_stack_modules = None
        self.stack_names = []
        self.stack_type = None
        self.stack_modules = {}

        self.use_special_modules = None
        self.special_modules_location = None

        self.service_template = None
        self.head_template = None

        self.forked_repo = 'n'
        self.already_forked = False
        self.git_user = 'robcxyz'
        self.repo = 'terragrunt-modules-'

        for d in args:
            for key in d:
                setattr(self, key, d[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @staticmethod
    def simple_question(question, default=None):
        prompt = '%s:' % (question)
        if not default:
            # prompt = f'{question}-\n[{default}]:'
            prompt = '%s-\n[%s]:' % (question, default)
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
        input_question = '%s-\n[%s]:' % (question, defaults)

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

    def ask_region(self):
        self.get_aws_availability_zones()
        self.possible_regions = self.availability_zones.keys()
        region = self.choice_question('Enter region number %d to deploy into? \n' % (self.r + 1),
                                      list(self.possible_regions))
        if region in self.regions:
            raise ValueError('Entered duplicate regions - exiting')
        self.regions.append(region)
        self.region = region
        self.stack[self.r] = {'region': region}
        self.stack[self.r] = {'modules': {}}

    def get_aws_availability_zones(self):
        if not self.got_az_list:
            self.rebuild_availability_zones = self.choice_question(
                'Would you like to update the availabilty zones list?',
                ['n', 'y'])
            if self.rebuild_availability_zones == 'y':
                write_availability_zones()
            with open(os.path.join(self.stacks_dir, '..', 'aws_availability_zones.json'), 'r') as f:
                self.availability_zones = json.load(f)
            self.got_az_list = True

    def ask_availability_zones(self):

        self.num_azs = self.choice_question('How many availability zones',
                                            ['1', '2', '3', '4', '5', '6', '7', 'max'])
        if self.num_azs == 'max':
            self.num_azs = len(self.availability_zones[self.region])
        else:
            self.num_azs = int(self.num_azs)
        if self.num_azs > len(self.availability_zones[self.region]):
            raise ValueError('Entered too many availability zones')

    def module_ask_module_location(self):
        # TODO:
        if self.use_common_modules == 'y' and not self.already_forked:
            self.forked_repo = self.choice_question('Do you have a private fork? \n '
                                                    '(I\'d fork it if you want to customize it ..)', ['n', 'y'])

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
            with open(os.path.join(self.stacks_dir, 'common.hcl'), 'r') as f:
                self.common_modules = hcl.load(f)
            # self.stack[self.r]['modules'] = StackParser(self.common_modules).stack['modules']
            modules = StackParser(self.common_modules).stack['modules']
            self.stack[self.r]['modules'].update(modules)

    def ask_stack_modules(self):

        self.use_stack_modules = self.choice_question('Do you want to use a generic stack?\n', ['y', 'n'])
        if self.use_stack_modules == 'y':
            stack_options = ['basic-p-rep', 'decoupled-p-rep', 'data-science', 'data-engineering-hadoop']
            self.stack_type = self.choice_question('What type of stack are you building?\n', stack_options)
            # TODO: Perhaps qualify the options first or allow for alternative input
            with open(os.path.join(self.stacks_dir, str(self.stack_type) + '.hcl')) as f:
                self.stack_modules = hcl.load(f)
            self.stack[self.r]['modules'].update(StackParser(self.stack_modules).stack['modules'])

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

        self.service_template = 'service' + str(self.terraform_version) + '.hcl'
        self.head_template = 'head' + str(self.terraform_version) + '.hcl'



    # def ask_templaetes_dir(self):
    #     if not self.debug:
    #         self.terraform_version = self.choice_question('What version of Terraform do you want to use?',
    #                                                       ['0.11', '0.12'])
    #     else:
    #         self.
    #     if self.terraform_version == '0.11':
    #         self.terraform_version = str(11)
    #         self.terragrunt_file = 'terraform.tfvars'
    #     else:
    #         self.terraform_version = str(12)
    #         self.terragrunt_file = 'terragrunt.hcl'

    def ask_all(self):
        for r in range(self.num_regions):
            self.r = r
            self.ask_region()
            self.stack[self.r] = {'region': self.region, 'modules': {}, 'files': {}}
            self.ask_availability_zones()
            self.ask_common_modules()
            self.ask_stack_modules()
            self.ask_special_modules()
            self.ask_terragrunt_version()

    # def init_all(self):

    @staticmethod
    def render_file():
        pass

    def make_all(self):

        env = Environment(loader=FileSystemLoader(self.templates_dir))

        # if not self.debug:
        #     # Must override in tests
        #     self.service_template = 'service' + str(self.terraform_version) + '.hcl'
        #     self.head_template = 'head' + str(self.terraform_version) + '.hcl'

        for r in range(self.num_regions):

            region_modules = self.stack[r]['modules'].keys()

            for m in region_modules:
                module_path = os.path.join(os.path.abspath(os.path.curdir), self.stack[r]['region'], m)
                os.makedirs(module_path)
                stack_dict = self.stack[r]['modules'][m]

                stack_dict.update({'is_service': True})  # TODO: This needs to be pulled out in the headless...

                env_tpl = env.get_template(self.service_template)
                rendered_file = env_tpl.render(stack_dict)
                # rendered_file = self.service_template.render(stack_dict)
                with open(os.path.join(module_path, self.terragrunt_file), 'w') as fp:
                    fp.write(rendered_file)

            # Make the path first
            region_path = os.path.join(os.path.abspath(os.path.curdir), self.stack[r]['region'])
            region_dict = {}  # TODO
            rendered_file = env.get_template(self.service_template).render(region_dict)
            # rendered_file = self.service_template.render(region_dict)
            with open(os.path.join(region_path, 'region.tfvars'), 'w') as fp:
                fp.write(rendered_file)

        env_dict = {}  # TODO
        rendered_file = env.get_template(self.head_template).render(env_dict)
        # rendered_file = self.service_template.render(env_dict)
        with open(os.path.join(os.path.curdir, '..', 'environment.tfvars'), 'w') as fp:
            fp.write(rendered_file)

        head_dict = {}  # TODO
        rendered_file = env.get_template(self.head_template).render(head_dict)
        # rendered_file = self.head_template.render(head_dict)
        with open(os.path.join(os.path.curdir, '..', self.terragrunt_file), 'w') as fp:
            fp.write(rendered_file)

    def main(self):
        if not self.headless:
            self.ask_all()
        self.make_all()


if __name__ == '__main__':
    shutil.rmtree('ap-northeast-1')

    # Context
    cc_trigger = '{{ cookiecutter.environment }}'
    if cc_trigger == '{{ cookiecutter.environment }}':
        tg = TerragruntGenerator(num_regions=1, debug=True)
        tg.main()
        print(tg.stack)
    else:
        tg = TerragruntGenerator(num_regions='{{ cookiecutter.num_regions }}', debug=False)
        tg.main()
