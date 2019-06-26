import json

from utils import write_availability_zones, get_availability_zones


REGIONS = ['ap-northeast-1', 'ap-northeast-2', 'ap-south-1', 'ap-southeast-1', 'ap-southeast-2', 'ca-central-1', 'eu-central-1', 'eu-north-1', 'eu-west-1', 'eu-west-2', 'eu-west-3']

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

        if self.num_regions > 1:
            self.ha = True
        else:
            self.ha = False

        self.rebuild_availability_zones = None
        self.regions = []
        self.num_azs = None
        self.use_common_modules = None
        self.availability_zones = None


        for d in args:
            for key in d:
                setattr(self, key, d[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @staticmethod
    def simple_question(question, default):
        try:
            user_entry = input(f'{question} - [{default}] :')
        except SyntaxError:
            user_entry = None
        if not user_entry:
            user_entry = default
        return user_entry

    @staticmethod
    def choice_question(question, defaults, list_output=False):
        """returns error when not in choices"""
        if not isinstance(defaults, list):
            raise ValueError("Default is not a list")
        choices = frozenset(defaults)
        input_question = f'{question} - [{defaults}] :'
        try:
            while True:
                # choice = raw_input().lower()
                user_entry = input(input_question)
                if user_entry in choices and not list_output:
                    break
                elif user_entry == "":
                    break
                else:
                    print("Option not available")
        except SyntaxError:
            # user_entry = None
            user_entry = defaults[0]
        # if not user_entry:
        #     user_entry = defaults[0]
        return user_entry

    @staticmethod
    def list_question(question, default):
        pass

    def ask_region(self):
        for r in range(self.num_regions):
            self.regions.append(self.choice_question('Which region would you like to deploy into?',['n', 'y']))

    def get_aws_availability_zones(self):
        self.rebuild_availability_zones = self.choice_question('Would you like to update the availabilty zones list?',
                                                               ['n', 'y'])
        if self.rebuild_availability_zones == 'y':
            write_availability_zones()
        with open('aws_availability_zones.json', 'r') as f:
            self.availability_zones = json.load(f)

    def ask_availability_zones(self):
        self.num_azs = self.choice_question('How many availability zones', ['1', '2', '3', '4', '5', '6', '7', 'max'])

    def ask_common_modules(self):
        self.use_common_modules = self.simple_question('Would you like to use common ', 1)

    def ask_all(self):
        pass

    def render(self):
        self.ask_all()


if __name__ == '__main__':
    # tg = TerragruntGenerator(debug=True).choice_question('How many availability zones', ['y', 'n'])

    tg = TerragruntGenerator(debug=True)
    tg.get_aws_availability_zones()
    print(tg.availability_zones['ap-northeast-1'])

