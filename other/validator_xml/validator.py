from lxml import etree

# Загрузка XML
xml = etree.parse("your_file.xml")

# Загрузка основной XSD схемы
xsd = etree.parse("your_schema.xsd")

# Создание валидатора
schema = etree.XMLSchema(xsd)

# Валидация
is_valid = schema.validate(xml)

if is_valid:
    print("XML is valid against the XSD schema.")
else:
    print("XML is not valid against the XSD schema.")
    print(schema.error_log)
