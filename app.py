import os
import psycopg2
import json
import uuid
from prettytable import PrettyTable

from datetime import datetime
import random

from flask import Flask, request, url_for, render_template
#from flask_cors import CORS

app = Flask(__name__)
#cors = CORS(app)

conn = psycopg2.connect(host='ec2-174-129-213-103.compute-1.amazonaws.com', port=5432, user='fepxmeilqyizmq', password='9x4u4WhrkiETKUcORi5Y-e-3ix', database='dbgl3jc6vv1h0c')
cursor = conn.cursor()

#dq = "DELETE FROM users WHERE (last_name='Constantino');"
#cursor.execute(dq)
#conn.commit()

# dataStr = '{ "users": [ {"uuid":"", "firstname": "Adam", "lastname":"Smith", "dob":"1985-07-12", "affiliation":"Alliance", "rank":"0", "elo":"1500"} ] }'
# data = json.loads(dataStr)
# data["users"][0]["uuid"] = str(uuid.uuid4())
# print data["users"]


def random_date():
  year = random.choice(range(1986, 1997))
  month = random.choice(range(1, 13))
  day = random.choice(range(1, 31))
  rd = datetime(year, month, day)
  return rd.strftime("%Y-%m-%d")


def getBracketCount():
    q = "SELECT COUNT(id) FROM brackets"
    cursor.execute(q)
    conn.commit()
    result = cursor.fetchone()[0]
    return result


def getUsers(count=0, rank=0, random=False):
    orderbyClause = ''
    if random == True:
        orderbyClause = "ORDER BY random() "

    limitClause = "LIMIT " + count
    rankClause = "WHERE (rank='" + str(rank) + "');"

    q = "SELECT * FROM users " + rankClause + orderbyClause + limitClause
    cursor.execute(q)
    conn.commit()
    return cursor.fetchall()

@app.route('/')
def hello():
    return "Dream BJJ app"

@app.route('/list')
def list():

    count = 0
    random = False
    rank = 0

    if 'count' in request.args:
        count = int(request.args['count'])

    if 'random' in request.args:
        random = True

    if 'rank' in request.args:
        rank = int(request.args['rank'])

    rows = getUsers(count, rank, random)
    cols = [x[0] for x in cursor.description]
    users = []
    for row in rows:
        user = {}
        for prop, val in zip(cols, row):
            user[prop] = str(val)
        users.append(user)

    jsonStr = '{ "competitors" : ' + str(users) + '}'
    jsonStr = jsonStr.replace("'", "\"")

    return jsonStr


@app.route('/generateBracketId/', methods=['GET'])
def generateBracketId():
    return str(getBracketCount())


@app.route('/brackets', methods=["GET", "POST"])
def brackets():
    bracket_table = PrettyTable(["id", "c1_id", "c2_id", "level", "result", "tournament_id"])
    bracket_table.align["id"] = 'l'
    bracket_table.padding_width = 1

    if request.method == 'POST':
        data = request.get_json(force=True)
        q = ''
        for b in data["brackets"]:
            id = getBracketCount()
            q = "INSERT INTO brackets(id,c1_id,c2_id,level,result,tournament_id) VALUES ('" + str(id) + "','" + str(b["c1_id"]) + "','" + str(b["c2_id"]) + "','" + str(b["level"]) + "','" + str(b["result"]) + "','" + str(b["tournament_id"]) + "');"
            ret = q
            cursor.execute(q)
            conn.commit()

    q = 'SELECT * FROM brackets;'
    cursor.execute(q)
    conn.commit()
    rows = cursor.fetchall()
    for row in rows:
        bracket_table.add_row(
            [str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4]), str(row[5])])

    return '<pre>' + str(bracket_table) + '</pre>'



@app.route('/generate_brackets', methods=["GET", "POST"])
def generate_bracket():



@app.route('/users/', methods=['GET', 'POST'])
def users():
    user_table = PrettyTable(["UUID", "First Name", "Last Name", "DOB", "Affiliation", "Rank", "ELO", "sex"])
    user_table.align["UUID"] = 'l'
    user_table.padding_width = 1
    form_string = ''

    if request.method == 'POST':
        dob = random_date()
        form_string = 'UUID: ' + str(uuid.uuid4()) + '<br>'
        form_string += 'First Name: ' + request.form['firstname'] + '<br>'
        form_string += 'Last Name: ' + request.form['lastname'] + '<br>'
        form_string += 'Affiliation: ' + request.form['affiliation'] + '<br>'
        #form_string += 'DOB: ' + request.form['dob'] + '<br>'
        form_string += 'DOB: ' + dob + '<br>'
        form_string += 'Rank: ' + request.form['rank'] + '<br>'
        form_string += 'Sex: ' + request.form['sex'] + '<br>'

        q = "INSERT INTO users(id,first_name,last_name,affiliation,dob,rank,elo,sex) VALUES ('" + str(uuid.uuid4()) + "', '" + request.form['firstname'] + "', '" + request.form['lastname'] + "', '" + request.form['affiliation'] + "', '" + dob + "', " + request.form['rank'] + ", 1500," + request.form['sex'] + ");"
        cursor.execute(q)
        conn.commit()

    q = 'SELECT * FROM users;'
    cursor.execute(q)
    conn.commit()
    rows = cursor.fetchall()
    for row in rows:
        user_table.add_row(
            [str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4]), str(row[5]), str(row[6]), str(row[7])])

    return '<pre>' + str(user_table) + '</pre><br><br>' + form_string + '<br><br>' + render_template('form_user.html')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
