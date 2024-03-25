import random

color = ['black','red','darkred','darkblue','green','darkgreen','blue','darkviolet']
data_list = []
new_list = list()
with open("data.txt", 'r') as data_text:
    data_list = data_text.readlines()
for i in data_list:
    full_string = ""
    i = i.replace("\n","")
    for j in i:
        if j != " " and j != "*":
            new_word = ""
            new_word = "%{" + f"color:{random.choice(color)}"+"}"+j+"% "
            full_string = full_string + new_word
        else:
            full_string = full_string + j
    full_string += "\n"
    new_list.append(full_string)

file_w = open('color_data.txt', "w")
file_w.seek(0)
for st in new_list:
    file_w.write(st)
file_w.close()