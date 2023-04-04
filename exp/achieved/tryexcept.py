try:
    raise IOError('content')
except IOError as e:
    print(e, 'at ioerr')
except Exception as e:
    print(e, 'at any')