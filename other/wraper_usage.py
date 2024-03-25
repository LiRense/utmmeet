import functools


def dark_theme(func):

    @functools.wraps(func)
    def wrap(*args,**kwargs):
        print('hello')
        return func(*args,**kwargs)
    return wrap()

@dark_theme
def home():
    print('home')