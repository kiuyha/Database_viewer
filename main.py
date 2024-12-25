from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os
from cryptography.fernet import Fernet
import requests
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

def request_api(script):
    print(script, flush=True)
    try:
        url = os.getenv('API_URL')
        response = requests.post(url, json={'api_key': session.get('api_key').decode(), 'script': script})
        return str(response.text), response.status_code
    except Exception as e:
        return str(e), 500

@app.route('/', methods=['GET'])
def page_login():
    if session.get('api_key'):
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    fernet = Fernet(os.getenv('SECRET_KEY').encode())
    email = request.form['email']
    password = request.form['password']
    api_key = fernet.encrypt((f"{email}|{password}").encode())
    session['api_key'] = api_key
    output, status = request_api("print('success')")
    if status == 200:
        return redirect(url_for('home'))
    else:
        session.pop('api_key', None)
        print(output)
        return output, status


@app.route('/home', methods=['GET'])
def home():
    if not session.get('api_key'):
        return redirect(url_for('page_login'))
    return render_template('home.html')


@app.route('/get_tables', methods=['GET'])
def get_tables():
    output, status = request_api("print(inspect(db.engine).get_table_names())")
    if status == 200:
        return jsonify(eval(output))
    return output, status


@app.route('/table/<table_name>', methods=['GET'])
def table(table_name):
    output, status = request_api(f'''
from .models import {table_name}
rows = {table_name}.query.all()
columns = [column.name for column in {table_name}.__table__.columns]
print({{'columns': columns,
'rows': [{{col: getattr(row, col) for col in columns}} for row in rows],
'type_data': {{ col: str({table_name}.__table__.columns[col].type) for col in columns }} }})
''')
    if status == 200:
        data = eval(output)
        print(data)
        return jsonify(data)  
    return output, status

@app.route('/delete_row/<table_name>/<row_id>', methods=['GET'])
def delete_row(table_name, row_id):
    output, status = request_api(f'''
from .models import {table_name}
row = {table_name}.query.filter_by(id={row_id}).first()
db.session.delete(row)
db.session.commit()
''')
    return jsonify(output), status

@app.route('/add_row/<table_name>', methods=['POST'])
def add_row(table_name):
    def parse_datetime(value):
        formats = ['%Y-%m-%d %H:%M:%S', '%a, %d %b %Y %H:%M:%S GMT', '%Y-%m-%d']
        for fmt in formats:
            try:
                return datetime.datetime.strptime(str(value), fmt).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
        return value
    data = request.get_json()
    output, status = request_api(f'''
from .models import {table_name}

data = {table_name}({', '.join([f"{key}={repr(parse_datetime(value))}" for key, value in data.items()])})
db.session.add(data)
db.session.commit()
    ''')
    return jsonify(output), status


@app.route('/update_row/<table_name>/<row_id>', methods=['POST'])
def update_row(table_name, row_id):
    data = request.get_json()
    output, status = request_api(f'''
from .models import {table_name}

def parse_datetime(value):
    formats = ['%Y-%m-%d %H:%M:%S', '%a, %d %b %Y %H:%M:%S GMT']
    for fmt in formats:
        try:
            return datetime.strptime(str(value), fmt).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue
    return value
row = {table_name}.query.filter_by(id={row_id}).first()
if row:
    for key, value in {data}.items():
        setattr(row, key, parse_datetime(value))
    db.session.commit()
''')
    return jsonify(output), status



@app.route('/logout', methods=['GET'])
def logout():
    session.pop('api_key', None)
    return redirect(url_for('page_login'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)