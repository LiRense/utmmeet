import ast

new_list1 = []
new_list2 = []
end_list = []
las_dic = {}
final = []
with open('new.txt','r') as file1:
    with open('pre_clear/new_lena.txt', 'r') as file2:
        lines1 = file1.readlines()
        lines2 = file2.readlines()
        for i in range(len(lines1)):
            new_list1.append(ast.literal_eval(lines1[i].replace('\n','')))
            new_list2.append(ast.literal_eval(lines2[i].replace('\n','')))
            end_list.append(new_list1[i])
            end_list.append(new_list2[i])
        print(end_list)
        for i in range(len(end_list)):
            las_dic[i] = [end_list[i][0]]
        print(las_dic)
        las_dic2 = {}
        sorted_dic = sorted(las_dic.items(), key=lambda item: item[1])
        print(sorted_dic)
        for i in sorted_dic:
            final.append(end_list[i[0]])
        print(final)
end = open('general_new.txt','w')
for i in final:
    end.writelines(str(i)+'\n')
end.close()
