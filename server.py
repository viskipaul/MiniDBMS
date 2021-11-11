from flask import Flask, request
from flask_cors import cross_origin, CORS
import re
import xml.etree.ElementTree as ET
import constants
from model.Attribute import Attribute
from model.ForeignKey import ForeignKey

app = Flask(__name__)
CORS(app)

@cross_origin()
@app.route('/default')
def main_controller():
    command = request.args.get('command')
    if re.search('(create database )[a-zA-Z]+', command):
        name = command.split(' ')[2]
        return create_database(name)
    elif re.search('(use database )[a-zA-Z]+', command):
        database_name = command.split(' ')[2]
        return use_database(database_name)
    elif re.search('(drop database )[a-zA-Z]+', command):
        database_name = command.split(' ')[2]
        return drop_database(database_name)
    elif re.search('(create table )[a-zA-Z()0-9]*', command):
        return create_table(command)
    elif re.search('(drop table )[a-zA-Z0-9]*', command):
        table_name = command.split(' ')[2]
        return drop_table(table_name)
    elif re.search('(create index )[a-zA-Z0-9.()]*', command):
        return create_index(command)
    elif re.search('(drop index )[a-zA-Z0-9.()]*', command):
        return drop_index(command)
    else:
        return "Invalid command."


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


def create_table(command: str) -> str:
    table_name, attributes, foreign_keys = validate_create_command(command)
    xml = ET.parse('database.xml')

    # Get current database
    f = open('current_database.txt', 'r')
    current_database = f.readline()
    print('Using database: ' + current_database + '.')

    existing_table = xml.find(".//Table[@tableName='" + table_name + "']")
    if existing_table:
        return 'Table already exists in the database.'

    table = ET.Element('Table')
    table.set('tableName', table_name)

    # Create Table tags
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
                        attr_xml = ET.Element('Attribute')
                        attr_xml.set('name', attribute.name)
                        attr_xml.set('type', attribute.type)
                        attr_xml.set('is_null', 'true' if attribute.is_null else 'false')
                        attr_xml.set('primary_key', 'true' if attribute.pk else 'false' )
                        table.append(attr_xml)
                        xml.write('database.xml')
                        print('1')
                    for key in foreign_keys:
                        fk_xml = ET.Element('ForeignKey')
                        fk_xml.set('attribute', key.attribute)
                        fk_xml.set('ref_attribute', key.ref_attribute)
                        fk_xml.set('ref_table', key.ref_table)
                        table.append(fk_xml)
                        print('2')
                xml.write('database.xml')

    return 'Succesfully created table ' + table_name + '.'


def drop_table(table_name: str) -> str:
    xml = ET.parse('database.xml')
    root = xml.getroot()
    existing_table = xml.getroot().find(".//Table[@tableName='" + table_name + "']")

    if not existing_table:
        return 'Table does not exist.'

    for db in root.findall('.//Database'):
        for table in db:
            if table.attrib.get('tableName') == table_name:
                db.remove(table)
                xml.write('database.xml')
                return 'Succesfully dropped table ' + table_name + '.'


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


if __name__ == '__main__':
    app.run(host="192.168.1.237")
