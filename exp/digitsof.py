def digitsof(s:str):
    return ''.join(list(filter(str.isdigit,list(s))))

print(digitsof('123ab'))
print(int(''))