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


def create_database(name) -> str:
    xml = ET.parse('database.xml')
    databases = xml.getroot()
    database = ET.Element('Database')
    database.set('name', name)
    databases.append(database)
    ET.dump(databases)
    xml.write('database.xml')
    return 'Succesfully created database ' + name + '.'


def use_database(name) -> str:
    f = open('current_database.txt', 'w')
    f.write(name)
    f.close()
    return 'Using database: ' + name + '.'


def drop_database(name) -> str:
    xml = ET.parse('database.xml')
    for elem in xml.iter():
        if elem.attrib.get('name') == name:
            xml.getroot().remove(elem)
    xml.write('database.xml')
    return 'Succesfully dropped database ' + name + '.'


def create_table(command: str) -> str:
    table_name, columns_dict = validate_create_command(command)
    xml = ET.parse('database.xml')



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
