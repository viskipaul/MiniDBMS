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


if __name__ == '__main__':
    app.run(host="192.168.1.237")
