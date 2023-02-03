from logging import exception


class clz:
    def __init__(self,p):
        self.p=p

para=15
src='{}(para)'.format('czlz')
try:
    obj=eval(src)
    print(obj)
    print(obj.p)
except BaseException as err:
    print('unknown type, {}'.format(err))