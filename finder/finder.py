with open("finder_1", 'r') as fd_1_list:
    fd_1 = fd_1_list.read().splitlines()
with open("finder_2", 'r') as fd_2_list:
    fd_2 = fd_2_list.read().splitlines()
fd_1_1 = list(set(fd_1))
fd_2_2 = list(set(fd_2))
print(fd_1_1)
print(fd_2_2)
for i in fd_1_1:
    if i in fd_2_2:
        print(fd_1_1.index(i)+1,'+',fd_2_2.index(i)+1, i)