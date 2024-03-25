import xml.etree.ElementTree as ET

# Загрузка XML-файла, экспортированного из draw.io
tree = ET.parse('diagram.xml')
root = tree.getroot()

uml_diagram = UMLDiagram()

# Пример обхода элементов XML-дерева и создания UML-структур
for elem in root.iter():
    if elem.tag == 'class':
        class_name = elem.attrib.get('name')
        new_class = Class(class_name)
        uml_diagram.add_class(new_class)
    elif elem.tag == 'relationship':
        class1 = elem.attrib.get('class1')
        class2 = elem.attrib.get('class2')
        relationship_type = elem.attrib.get('type')
        new_relationship = Relationship(class1, class2, relationship_type)
        uml_diagram.add_relationship(new_relationship)

# Генерация UML-диаграммы
uml_diagram.render('output.png')