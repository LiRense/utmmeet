import matplotlib.pyplot as plt
import json

def AVG(lst):
    return sum(lst) / len(lst)

with open('new.txt', 'r') as file:
    files = file.read().splitlines()

new = []
for i in files:
    res = json.loads(i)
    new.append(res)

print(new)
x=[]
y=[]
for i in new:
    x.append(i[0])
    y.append(i[1])
print(x)
print(y)

print('# Результаты нагрузочного тестирования на новой версии')
print('<pre>')
print('Кол-во запросов:', len(new))
print('Время обработки:',max(x),'сек')
print('Минимальное время ответа:',min(y),'сек','\nМаксимальное время ответа:',max(y),'сек','\nСреднее время ответа:',AVG(y),'сек')
print("Кол-во запросов в 1 секунду", len(new)/max(x))
print('</pre>')
print('{{collapse(График ответов)\n\n}}')
plt.plot(x,y)
plt.show()
