import random

for i in range(1000):
    x = random.randint(1,9999999)
    if len(str(x)) < 7:
        print(x)