with open("xml/xml_before", 'r') as xml_list:
    before_list = xml_list.readlines()
for i in range(len(before_list)):
    if "\n" in before_list[i] != 0:
        print(0,before_list[i])
        break
    else:
        print(1,before_list)
        break