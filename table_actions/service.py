from .validations import validate_create_command, create_table_attribute, table_exists, create_table_fk
import xml.etree.ElementTree as ET
import constants
from model.Attribute import Attribute
from model.ForeignKey import ForeignKey


def create_table(command: str) -> str:
    table_name, attributes, foreign_keys = validate_create_command(command)
    xml = ET.parse('database.xml')

    # Get current database
    f = open('current_database.txt', 'r')
    current_database = f.readline()
    print('Using database: ' + current_database + '.')

    if table_exists(table_name, xml):
        return 'Table already exists in the database.'

    table = ET.Element('Table')
    table.set('tableName', table_name)

    for elem in xml.iter():
        if elem.attrib.get('name') == current_database:
            elem.append(table)
            xml.write('database.xml')

    xml = ET.parse('database.xml')
    root = xml.getroot()

    for database in root.iter():
        if database.attrib.get('name') == current_database:
            for table in database.iter():
                if table.attrib.get('tableName') == table_name:
                    for attribute in attributes:
                        attr_xml = create_table_attribute(attribute)
                        table.append(attr_xml)
                        xml.write('database.xml')
                    for fk in foreign_keys:
                        fk_xml = create_table_fk(fk)
                        table.append(fk_xml)
                xml.write('database.xml')

    return 'Succesfully created table ' + table_name + '.'


def drop_table(table_name: str) -> str:
    xml = ET.parse('database.xml')
    root = xml.getroot()
    existing_table = table_exists(table_name, xml)

    if not existing_table:
        return 'Table does not exist.'

    for db in root.findall('.//Database'):
        for table in db:
            if table.attrib.get('tableName') == table_name:
                db.remove(table)
                xml.write('database.xml')
                return 'Succesfully dropped table ' + table_name + '.'
