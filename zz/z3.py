import xml.etree.ElementTree as et
import requests as rq

# с немспейсами
ns = '{http://fsrar.ru/WEGAIS/WB_DOC_SINGLE_02}'
cq = '{http://fsrar.ru/WEGAIS/Cheque}'
root = et.Element(ns + 'Document')
et.SubElement(root, cq + 'Bottle').text = 'some 1'
et.SubElement(root, ns + 'Bottle').text = 'some 2'
et.dump(root)
# отправка
# можно слать сразу в песок
netty = 'http://194.67.93.217:14206/wb'
xml = et.tostring(root, encoding="unicode", method="xml")
# xmlutf = xml.decode("utf-8")
xmlfile = {'file': xml}
resp = rq.post(netty, files=xmlfile)
print(resp.text)
# можно затем сразу разбирать ответ
outroot = et.fromstring(resp.text)
btls = outroot.findall(cq + 'Bottle')
for bo in btls:
    print(bo.attrib['barcode'], bo.find(cq + 'Form2').text)