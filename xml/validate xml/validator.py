# from lxml import etree
#
# def validate(xml_path: str, xsd_path: str) -> bool:
#
#     xmlschema_doc = etree.parse(xsd_path)
#     xmlschema = etree.XMLSchema(xmlschema_doc)
#
#     xml_doc = etree.parse(xml_path)
#     result = xmlschema.validate(xml_doc)
#
#     return result
#
# print(validate("xml","xsd1.xsd"))
import


xmlgenerator = XMLGenerator('resources/pain.001.001.09.xsd1.xsd', True, DataFacet())
print(xmlgenerator.execute()) # Output to console
xmlgenerator.write('filename.xml') # Output to file