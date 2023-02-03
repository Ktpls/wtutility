
class clz:
    val=1

def foo(p):
    c=p['c']
    c.val+=1
    print(p['c'].val)

c=clz()
foo(globals())
foo(globals())