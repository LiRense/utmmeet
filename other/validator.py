from string import *
from xmlschema import *
from random import *
from xml.etree.ElementTree import *
import requests

schema_xsd = XMLSchema('/home/ivan/Рабочий стол/xsd-схема.xsd')
t = parse('/home/ivan/Рабочий стол/test.xml')
result = schema_xsd.is_valid(t)
if result == True:
    print('Document is valid? {}'.format(result))
    files = {
        'file': open('/home/ivan/Рабочий стол/test.xml', 'rb'),
    }
else:
    print('Document is valid? {}'.format(result))
