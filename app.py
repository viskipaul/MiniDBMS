from flask import Flask, request
from flask_cors import cross_origin, CORS
import re
import xml.etree.ElementTree as ET

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
    table_name, columns_dict = validate_create_command(command)
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
                    for attr_name in columns_dict:
                        attribute = ET.Element('Attribute')
                        attribute.set('name', attr_name)
                        attribute.set('type', columns_dict[attr_name])
                        table.append(attribute)
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


def validate_create_command(command: str):
    table_name = command.split(' ')[2]
    columns = command.split(' ( ')[1]
    columns_list = columns.split(',')
    columns_dict = {}
    for column in columns_list:
        columns_dict[column.strip().split(' ')[0]] = column.strip().split(' ')[1]
    return table_name, columns_dict


if __name__ == '__main__':
    app.run(host="192.168.1.237")
