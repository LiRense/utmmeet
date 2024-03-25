import xmltodict
import json
# uri = input("Введите URI: ") #/home/ivan/PycharmProjects/utmmeet/zz/1.xml
uri = '/home/ivan/PycharmProjects/utmmeet/zz/1.xml'
with open(uri,"r") as file_uri:
    xml = file_uri.read()
    python_dict = xmltodict.parse(xml)
    json_string = json.dumps(python_dict)




print(json_string)