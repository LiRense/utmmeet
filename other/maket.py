s = 'MCMXCIV'
def twoSum(s):
    x = {'I': ' 1',
         "V": ' 5',
         "X": ' 10',
         "L": ' 50',
         "C": ' 100',
         "D": ' 500',
         'M': ' 1000'}
    for key in x.keys():
        s = s.replace(key,x[key])
        print(s)
    s = s.split()
    s = list(map(int, s))
    print(s)
    sum = s[0]
    for i in range(1,len(s)):
        if s[i] < s[i-1]:
            sum -=s[i]
        else:
            sum+=s[i]

    return s

end = twoSum(s)
print(end)