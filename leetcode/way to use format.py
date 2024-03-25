def converter(s):
    dictionary ={
        'mile':1609,
        'yard':0.9144,
        'foot':0.3048,
        'inch':0.0254,
        'km':1000,
        'm':1,
        'cm':0.01,
        'mm':0.001
    }
    s_list = s.split(" ")
    s_list.remove('in')
    n = float(s_list[0]) * dictionary[s_list[1]] / dictionary[s_list[2]]
    return f'{n:.2e}'


s = '15.5 mile in km'
print(converter(s))
