
import itertools
import re


def generateDataObject(name, *scope):
    codetemplate_mainbody =\
        '''
class {}:
\tdef __init__(self{}):
{}
'''
    initparalist = ''.join([','+s for s in scope]) if len(scope) > 0 else ''

    codetemplate_initvaluelist =\
        '''\t\tself.{}={}'''
    initsetvaluelist = '\n'.join(
        [codetemplate_initvaluelist.format(s, s) for s in scope])
    code = codetemplate_mainbody.format(name, initparalist, initsetvaluelist)
    return code


def savecode(name, code: str):
    with open(f'{name}.py', mode='wb+') as f:
        f.write(code.encode('utf-8'))


def generateFileWithList(filename, l):
    l = [generateDataObject(*i) for i in l]
    code = ''.join(l)
    savecode(filename, code)


dolist = [
    ['doInput', 'id', 'i'],
    ['doTest2', 'scope', 'scope2'],
]
generateFileWithList('adogoutput', dolist)
