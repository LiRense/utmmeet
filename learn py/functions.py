from functools import reduce

func_lambda = lambda x: x**x

dic = {'func_lambda':func_lambda}
# print(dic['func2'](7))

lis = [1,2,3,4,5,6,7,8,9,10]

# print(list(map(func_lambda,lis)))


def filter_odd_num(in_num):
    if(in_num % 2) == 0:
        return True
    else:
        return False

# print(list(filter(filter_odd_num,lis)))


factorial = 9
lis2 = [i for i in range(1,factorial+1)]
lis3 = [i for i in range(factorial,0,-1)]
# print(reduce(lambda x,y:x*y,lis2))

print(list(lis3.__reversed__()))
print()
print(tuple(zip(lis,lis2)))