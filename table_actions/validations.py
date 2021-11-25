import xml.etree.ElementTree as ET
import constants
from model.Attribute import Attribute
from model.ForeignKey import ForeignKey

def validate_create_command(command: str):
    # Determine the table name from the command
    create_intro = command.split('(')[0]
    table_name = create_intro.split(' ')[2]
    print("Table name: ", table_name)

    # Determine the attributes and their properties from the command
    create_attrs = command.split('(')[1]
    print("Create attrs: ", create_attrs)
    attrs = create_attrs.split(',')
    print("Attrs: ", attrs)
    resulted_attributes = []
    resulted_fks = []
    for attr in attrs:
        # Setting default values for primary_key and not_null constraints
        attr_pk = False
        attr_is_null = True
        attr_name = ''
        attr_type = ''
        fk_reference = ''
        fk_table = ''
        fk_attribute = ''

        keywords = attr.split(' ')
        keywords = [keyword for keyword in keywords if not keyword == '']
        print('Keywords: ', keywords)
        for i in range(len(keywords)):
            next_keyword = ""
            keyword = keywords[i].strip("() ")
            if i < len(keywords) - 1:
                next_keyword = keywords[i+1].strip("() ")
            if i == 0:
                attr_name = keyword
            if keyword in constants.data_types:
                attr_type = keyword
            elif next_keyword and keyword.lower() == 'primary' and next_keyword.lower() == 'key':
                attr_pk = True
            elif next_keyword and keyword.lower() == 'not' and next_keyword.lower() == 'null':
                attr_is_null = False
            elif keyword == 'foreign' and next_keyword == 'key' and keywords[i+2] == 'references':
                fk_table = keywords[i+3]
                fk_reference = keywords[i+4]
                fk_attribute = attr_name
        if attr_name and attr_type:
            if not fk_reference == '':
                resulted_fk = ForeignKey(fk_attribute, fk_table, fk_reference)
                resulted_fks.append(resulted_fk)

            resulted_attribute = Attribute(attr_name, attr_type, attr_pk, attr_is_null)
            print("Resulted attribute: ", resulted_attribute.name)
            resulted_attributes.append(resulted_attribute)

    return table_name, resulted_attributes, resulted_fks


def create_table_attribute(attribute):
    attr_xml = ET.Element('Attribute')
    attr_xml.set('name', attribute.name)
    attr_xml.set('type', attribute.type)
    attr_xml.set('is_null', 'true' if attribute.is_null else 'false')
    attr_xml.set('primary_key', 'true' if attribute.pk else 'false')
    return attr_xml


def table_exists(table_name, xml) -> bool:
    existing_table = xml.find(".//Table[@tableName='" + table_name + "']")
    return existing_table


def create_table_fk(key):
    fk_xml = ET.Element('ForeignKey')
    fk_xml.set('attribute', key.attribute)
    fk_xml.set('ref_attribute', key.ref_attribute)
    fk_xml.set('ref_table', key.ref_table)
    return fk_xml
