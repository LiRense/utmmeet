import re
pattern = re.compile(r'([1-9]\d{2}|\d([1-9]\d|\d[1-9])){2}([1-9]\d{7}|\d([1-9]\d{6}|\d([1-9]\d{5}|\d([1-9]\d{4}|\d([1-9]\d{3}|\d([1-9]\d{2}|\d([1-9]\d|\d[1-9])))))))(0[1-9]|1[0-2])(1[8-9]|[2-9][0-9])([1-9]\d{2}|\d([1-9]\d|\d[1-9]))[0-9A-Z]{129}|\d\d[a-zA-Z0-9]{21}\d[0-1]\d[0-3]\d{10}[a-zA-Z0-9]{31}|[0-9]{40}')
str = u''
print(pattern.search(str))