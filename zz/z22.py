import xml.etree.ElementTree as et
from z13 import Barcode
from random import  randint
import z11

def gen_bcs():
    anotherattr=dict()
    barcode = Barcode()
    rand_num = randint(0,2)
    if rand_num == 0:
        anotherattr["Barcode"] = barcode.getold(1)
    elif rand_num == 1:
        anotherattr["Barcode"] = barcode.getnew(1)
    elif rand_num == 2:
        for i in range(randint(1,5)):
            anotherattr["Nomark_"+str(i)] = z11.Generator().gen_vers(randint(1,15))
    return anotherattr

# attr = {}
# attr['a1'] = 'b2'
root = et.Element('Cheque')

max_bc = randint(1,20)
for i in range(max_bc):
    el = et.SubElement(root, 'Position_'+ str(i+1), attrib=gen_bcs())
    xml = et.tostring(root, encoding="utf-8", method="xml")
    xml = xml.decode("utf-8") # to var
et.dump(root)

f = open('1.xml', 'w')
f.write(xml)
f.close()
print(xml)