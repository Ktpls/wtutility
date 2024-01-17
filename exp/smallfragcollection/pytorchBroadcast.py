import torch as th
a=th.tensor([
    [1,1,1],
    [0,0,0]
    ])
b=th.tensor(
    [[1],[0]])

c=a-b
print(c)