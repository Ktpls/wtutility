from utilref import *


aq=AccessibleQueue(3)
def printAq():
    print(aq[:])
    
print('fill')
i=0
while not aq.isFull():
    aq.push(i)
    i+=1
    printAq()

print('full')
try:
    aq.push(i)
except aq.AQException as e:
    print(e)
printAq()

print('pop')
for j in range(2):
    aq.pop()
    printAq()

print('resize')
aq.resize(5)
while not aq.isFull():
    aq.push(i)
    i+=1
    printAq()

print('rev iter')
j=-1
while j>=-len(aq):
    print(aq[j], end=", ")
    j-=1
print(end="\n")