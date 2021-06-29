from flask import Flask, request, make_response, Response, jsonify
import psycopg2
import psycopg2.extras
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from psycopg2 import IntegrityError
import secrets
import string
import hashlib

app = Flask(__name__)
app.secret_key = "thisisgarvitjainsecretkey"
jwt = JWTManager(app)

DB_HOST = "172.17.0.2"
DB_NAME = "sampledb"
DB_USER = "postgres"
DB_PASS = "root"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)



@app.route('/register', methods=['POST'])
def register():
 try:
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if not username:
        return 'Missing email', 400
    if not password:
        return 'Missing password', 400
    salt=salt_generator()
    new_pass = password + str(salt)
    hashed = hashlib.sha256(new_pass.encode()).hexdigest()

    cur.execute("INSERT INTO users (username, passwrd, salt) VALUES (%s,%s,%s)",(username, str(hashed),str(salt)))
    conn.commit()

    return { "message": "successfully registered"}, 200
 except IntegrityError:
    conn.session.rollback()
    return 'User Already Exists', 400
 except AttributeError:
    return 'Provide an Username and Password in JSON format in the request body', 400


@app.route('/login', methods=['POST'])
def login():

        username =  request.json.get('username', None)
        passw =  request.json.get('password', None)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if not username:
            return 'Missing username', 400
        if not passw:
            return 'Missing password',
        #cur.execute('SELECT salt FROM login WHERE email = {0}'.format(id))
        cur.execute(""" SELECT salt FROM users WHERE username = %s;""", [username, ])
        salt_value = cur.fetchone()
        salt_value = str(salt_value[0])
        new_pass= passw + salt_value
        hashed = hashlib.sha256(new_pass.encode()).hexdigest()

        cur.execute(""" SELECT * FROM users WHERE username = %s AND passwrd = %s ;""", [username,str(hashed),])
        user = cur.fetchone()

        if not user:
            return 'User Not Found!', 404
        else:
            access_token = create_access_token(identity={"username": username})
            return {"access_token": access_token}, 200

@app.route('/getListOfAllStudent',  methods = ['GET'])
@jwt_required()
def homePage():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s = "SELECT * FROM students"
    cur.execute(s)  # Execute the SQL
    list_users = cur.fetchall()

    return make_response(jsonify({"student_list": list_users}))


@app.route('/addIndividualStudent', methods=['POST'])
@jwt_required()
def add_student():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        data = request.get_json()
        cur.execute("INSERT INTO students (fname, lname, email) VALUES (%s,%s,%s)", (data['fname'], data['lname'], data['email']))
        conn.commit()
        return Response('student added successfully',status=201,content_type='text')


@app.route('/getById/<id>', methods=['POST', 'GET'])
@jwt_required()
def get_employee(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM students WHERE id = %s', (id))
    data = cur.fetchall()
    cur.close()
    return make_response(jsonify({"student_list": data[0]}))


@app.route('/updateById/<id>', methods=['PUT'])
@jwt_required()
def update_student(id):
    if request.method == 'PUT':
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        data = request.get_json()
        cur.execute("""
            UPDATE students
            SET fname = %s,
                lname = %s,
                email = %s
            WHERE id = %s
        """, (data['fname'], data['lname'], data['email'], id))
        conn.commit()
        return Response('student updated successfully', status=201, content_type='text')


@app.route('/deleteById/<string:id>', methods=['DELETE'])
@jwt_required()
def delete_student(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute('DELETE FROM students WHERE id = {0}'.format(id))
    conn.commit()
    return Response('student deleted successfully', status=201, content_type='text')


'</string:id></id></id>'


def salt_generator():
    string_source = string.ascii_letters + string.digits + string.punctuation
    password = secrets.choice(string.ascii_lowercase)
    password += secrets.choice(string.ascii_uppercase)
    password += secrets.choice(string.digits)
    password += secrets.choice(string.punctuation)

    for _ in range(6):
        password += secrets.choice(string_source)

    char_list = list(password)
    secrets.SystemRandom().shuffle(char_list)
    password = ''.join(char_list)
    return password

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
