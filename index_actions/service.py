import xml.etree.ElementTree as ET

def create_index(command: str) -> str:
    command_list = command.split(' ')
    index_name = command_list[2]
    table_name = command_list[4]
    field_names = command_list[5]
    field_names = field_names.strip('() ')
    fields = field_names.split(',')

    f = open('current_database.txt', 'r')
    current_database = f.readline()
    print('Using database: ' + current_database + '.')

    xml = ET.parse('database.xml')
    root = xml.getroot()
    for database in root.iter():
        if database.attrib.get('name') == current_database:
            for table in database:
                print('Table: ', table)
                if table.attrib.get('tableName') == table_name:
                    print('Found table')
                    index_xml = ET.Element('Index')
                    index_xml.set('indexName', index_name)
                    index_xml.set('unique', '0')
                    for field in fields:
                        indexfield_xml = ET.Element('IndexAttribute')
                        indexfield_xml.set('attributeName', field)
                        index_xml.append(indexfield_xml)
                    table.append(index_xml)
    xml.write('database.xml')
    return 'Succesfully created index ' + index_name + '.'


def drop_index(command: str) -> str:
    pass