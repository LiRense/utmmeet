def fizzbuzz(one,two):
    fb_list = []
    for i in range(one,two+1):
        if i % 3 == 0 and i % 5 == 0:
            i = 'FizzBuzz'
        elif i%3 == 0:
            i = 'Fizz'
        elif i%5 == 0:
            i = 'Buzz'
        print(i)




onew = input()
onews = onew.split()
one = int(onews[0])
two = int(onews[1])
fizzbuzz(one,two)