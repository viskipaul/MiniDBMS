import xml.etree.ElementTree as ET

def create_database(name) -> str:
    xml = ET.parse('database.xml')
    databases = xml.getroot()

    # Checking if database already exists
    for database in databases.iter():
        if database.get('name') == name:
            return 'Database ' + name + ' already exists.'

    database = ET.Element('Database')
    database.set('name', name)
    databases.append(database)
    ET.dump(databases)
    xml.write('database.xml')

    return 'Succesfully created database ' + name + '.'


def use_database(name) -> str:
    f = open('current_database.txt', 'w')
    xml = ET.parse('database.xml')
    for elem in xml.iter():
        if elem.attrib.get('name') == name:
            f.write(name)
            f.close()
            return 'Using database ' + name + '.'
    return 'Database ' + name + ' does not exist.'


def drop_database(name) -> str:
    xml = ET.parse('database.xml')
    for elem in xml.iter():
        if elem.attrib.get('name') == name:
            xml.getroot().remove(elem)
            xml.write('database.xml')
            return 'Succesfully dropped database ' + name + '.'
    return 'Database ' + name + ' does not exist.'
