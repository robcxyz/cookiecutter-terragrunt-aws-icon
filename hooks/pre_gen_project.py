import os
import json
import hcl

from utils import write_availability_zones, StackParser

REGIONS = ['ap-northeast-1', 'ap-northeast-2', 'ap-south-1', 'ap-southeast-1', 'ap-southeast-2', 'ca-central-1',
           'eu-central-1', 'eu-north-1', 'eu-west-1', 'eu-west-2', 'eu-west-3']


class TerragruntGenerator(object):

    def __init__(self, environment='dev', num_regions=1, debug=False, headless=False, *args, **kwargs):
        self.debug = debug
        self.headless = headless
        self.stacks_dir = os.path.join(os.path.abspath(os.path.curdir), '..', 'hooks', 'stacks')

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
        prompt = '%s:'.format(question)
        if not default:
            # prompt = f'{question}-\n[{default}]:'
            prompt = '%s-\n[%s]:'.format(question, default)
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
        input_question = '%s-\n[%s]:'.format(question, defaults)

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
        region = self.choice_question('Enter region number %d to deploy into? \n'.format(self.r + 1),
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
            self.stack[self.r]['modules'].update(StackParser(self.common_modules).stack['modules'])

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

    def ask_all(self):
        for r in range(self.num_regions):
            self.r = r
            self.ask_region()
            self.stack[self.r] = {'region': self.region, 'modules': {}, 'files': {}}
            self.ask_availability_zones()
            self.ask_common_modules()
            self.ask_stack_modules()
            self.ask_special_modules()

    def make_all(self):
        for r in range(self.num_regions):
            region_modules = self.stack[r]['modules'].keys()
            # for m in range(len(region_modules)):
            for m in region_modules:
                module_path = os.path.join(os.path.abspath(os.path.curdir), self.stack[r]['region'], m)
                os.makedirs(module_path)

    def main(self):
        if not self.headless:
            self.ask_all()
        self.make_all()

if __name__ == '__main__':
    tg = TerragruntGenerator(num_regions=1, debug=True)
    tg.main()
    print(tg.stack)
