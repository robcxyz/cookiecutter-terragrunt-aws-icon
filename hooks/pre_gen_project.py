

class TerragruntGenerator(object):

    def __init__(self, debug=False):
        self.debug = debug
        # These values need override to pass tests instead of rendering them
        if self.debug:
            self.environment = 'dev'
            self.num_regions = int(1)
        else:
            self.environment = '{{ cookiecutter.environment }}'
            self.num_regions = int('{{ cookiecutter.num_regions }}')

        if self.num_regions > 1:
            self.ha = True
        else:
            self.ha = False

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
    def choice_question():
        pass

    def ask_availability_zones(self):
        self.num_azs = self.simple_question('How many availability zones', 1)

    def ask_common_modules(self):

        self.use_common_modules = self.simple_question('Would you like to use common ', 1)

    def ask_all(self):
        pass

    def render(self):
        self.ask_all()



if __name__ == '__main__':
    tg = TerragruntGenerator()
