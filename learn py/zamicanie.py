def make_adder():

    n = 0

    def fn(x):
        nonlocal n

        n += x
        return n

    return fn

my_fn = make_adder()

print(my_fn(2))
print(my_fn(2))