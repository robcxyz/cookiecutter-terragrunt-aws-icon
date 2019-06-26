import os
import json
import hcl

from utils import write_availability_zones, get_availability_zones

REGIONS = ['ap-northeast-1', 'ap-northeast-2', 'ap-south-1', 'ap-southeast-1', 'ap-southeast-2', 'ca-central-1',
           'eu-central-1', 'eu-north-1', 'eu-west-1', 'eu-west-2', 'eu-west-3']


class TerragruntGenerator(object):

    def __init__(self, environment='dev', num_regions=1, debug=False, *args, **kwargs):
        self.debug = debug
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
        prompt = f'{question}:'
        if not default:
            prompt = f'{question}-\n[{default}]:'
        try:
            user_entry = input(prompt)
        except SyntaxError:
            user_entry = None
        if not user_entry and default is not None:
            user_entry = default
        if not user_entry and default is None:
            # simple_question()
            raise ValueError
        return user_entry

    @staticmethod
    def choice_question(question, defaults):
        """returns error when not in choices"""
        if not isinstance(defaults, list):
            raise ValueError("Default is not a list")
        choices = frozenset(defaults)
        input_question = f'{question}-\n[{defaults}]:'
        try:
            while True:
                # choice = raw_input().lower()
                user_entry = input(input_question)
                if user_entry in choices:
                    break
                elif user_entry == "":
                    break
                else:
                    print("Option not available")
        except SyntaxError:
            user_entry = None
        if not user_entry:
            user_entry = defaults[0]
        return user_entry

    def ask_region(self):
        self.get_aws_availability_zones()
        self.possible_regions = self.availability_zones.keys()
        # for r in range(self.num_regions):
        region = self.choice_question(f'Enter region number {self.r + 1} to deploy into? \n',
                                      list(self.possible_regions))
        if region in self.regions:
            raise ValueError('Entered duplicate regions - exiting')
        self.regions.append(region)
        self.region = region
        self.stack[self.r] = {'region': region}

    def get_aws_availability_zones(self):
        if not self.got_az_list:
            self.rebuild_availability_zones = self.choice_question(
                'Would you like to update the availabilty zones list?',
                ['n', 'y'])
            if self.rebuild_availability_zones == 'y':
                write_availability_zones()
            with open('aws_availability_zones.json', 'r') as f:
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

    def ask_common_modules(self):
        self.use_common_modules = self.choice_question('Would you like to use common modules', ['y', 'n'])
        if self.use_common_modules == 'y' and not self.already_forked:
            self.forked_repo = self.choice_question('Do you have a private fork? \n '
                                                    '(I\'d fork it if you want to customize it ..)', ['y', 'n'])
        if self.forked_repo == 'y' and not self.already_forked:
            self.git_user = self.simple_question('What is your github username / organization?', ['y', 'n'])
            self.already_forked = True

        if self.use_common_modules == 'y':
            common_path = os.path.join('data', 'common.hcl')
            with open(common_path, 'r') as f:
                self.common_modules = hcl.load(f)

    def ask_stack_modules(self):
        self.use_stack_modules = self.choice_question('What kind of stack are you building?\n',
                                                      ['basic-p-rep', 'decoupled-p-rep', 'data-science',
                                                       'data-engineering-hadoop'])
        data_dir = os.path.join(os.path.abspath(os.path.curdir), 'data')
        print(type(data_dir))
        self.stack_names = os.listdir(data_dir)
        # print(data_dir.remove('common.hcl'))


    def ask_special_modules(self):
        self.use_special_modules = self.choice_question('', ['y', 'n'])

        for r in range(self.num_regions):
            self.r = r
            self.ask_region()
            self.ask_availability_zones()
            self.ask_common_modules()


    def render(self):
        self.ask_all()


if __name__ == '__main__':
    # tg = TerragruntGenerator(debug=True).choice_question('How many availability zones', ['y', 'n'])
    tg = TerragruntGenerator(num_regions=2, debug=True)
    tg.ask_stack_modules()
    print(tg.stack_names)

