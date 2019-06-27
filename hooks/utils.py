import hcl

from pprint import pprint

from pre_gen_project import StackParser

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
