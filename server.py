from flask import Flask, request
from flask_cors import cross_origin, CORS
import re

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


if __name__ == '__main__':
    app.run(host="192.168.1.237")
