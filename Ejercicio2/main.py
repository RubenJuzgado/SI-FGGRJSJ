import json
import sqlite3
from sqlite3 import Error


def create_connection(database):
    conn = None
    try:
        conn = sqlite3.connect(database)
        return conn
    except Error as e:
        print(e)


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


# def save_data(data):
#   conn = connect()
#  cur = conn.cursor()
# cur.execute('insert into USERS(data) values(%s)', (data,))
# conn.commit()
# conn.close()


# def load_data(id):
#    conn = connect()
#    cur = conn.cursor()
#    cur.execute('SELECT * FROM USER WHERE nombre = %s', (id,))
#    datos = cur.fetchone()
#    conn.close()
#    return datos


def main():
    # legalJSON = json.load(open('legal.json', 'r'))
    # usersJSON = json.load(open('users.json', ))
    # usersdata = json.load(usersJSON)
    # USERS
    conn = create_connection('bd.db')
    cursor = conn.cursor()
    create_emails = """create table EMAILS (id integer primary key, totals int, phishing int, cliclados int)"""
    create_table(conn, create_emails)
    create_ips = """create table IPS (id integer primary key autoincrement, ip varchar(255) )"""
    create_table(conn, create_ips)
    create_fechas = """create table FECHAS (id integer primary key autoincrement, fecha varchar(255))"""
    create_table(conn, create_fechas)
    create_users = """create table USERS (nombre varchar(255) primary key, telefono int(9),contrasena varchar(255),provincia varchar(255),permisos varchar(255), emails, FOREIGN KEY (emails) references EMAILS(id))"""
    create_table(conn, create_users)
    create_userToFechas = """create table USERSTOFECHAS (id integer primary key autoincrement, fecha_user varchar(255), nombre_users varchar(255), FOREIGN KEY (fecha_user) references FECHAS(fecha), FOREIGN KEY (nombre_users) REFERENCES USERS(nombre))"""
    create_table(conn, create_userToFechas)
    create_userToIPS = """create table USERSTOIPS (id integer primary key autoincrement, ip_user varchar(255), nombre_users varchar(255), FOREIGN KEY (ip_user) references IPS(ip), FOREIGN KEY (nombre_users) REFERENCES USERS(nombre))"""
    create_table(conn, create_userToIPS)
    create_legal = """create table WEBS (nombre varchar(255) primary key, cookies int,aviso int, proteccion_de_datos int, creacion int)"""
    create_table(conn, create_legal)

    users = json.load(open('users.json'))
    webs = json.load(open('legal.json'))

    """for email in users['usuarios']['emails']:
        print(email)

    for user in users['usuarios']:
        print(user)
        cursor.execute("Insert into USERS values (?, ?, ?, ?, ?, ?, ?)", (user, user['telefono'], user['contrasena'], user['provincia'],user['permisos'], user['emails'], user))
    """
    for i in range(len(webs['legal'])):
        for web in webs['legal'][i].keys():
            cursor.execute("Insert into WEBS values (?, ?, ?, ?, ?)", (web, webs['legal'][i][web]['cookies'], webs['legal'][i][web]['aviso'], webs['legal'][i][web]['proteccion_de_datos'], webs['legal'][i][web]['creacion']))
            conn.commit()
    for i in range(len(users['usuarios'])):
        for user in users['usuarios'][i].keys():
            cursor.execute("Insert into EMAILS values (?, ?, ?, ?)", (i, users['usuarios'][i][user]['emails']['total'], users['usuarios'][i][user]['emails']['phishing'], users['usuarios'][i][user]['emails']['cliclados']))
            conn.commit()
            cursor.execute("Insert into USERS values (?, ?, ?, ?, ?, ?)", (user, users['usuarios'][i][user]['telefono'], users['usuarios'][i][user]['contrasena'], users['usuarios'][i][user]['provincia'], users['usuarios'][i][user]['permisos'], i))
            conn.commit()
            for j in range(len(users['usuarios'][i][user]['fechas'])):
                cursor.execute("Insert into FECHAS(fecha) values (?)", (users['usuarios'][i][user]['fechas'][j],))
                conn.commit()
                cursor.execute("Insert into  USERSTOFECHAS(fecha_user, nombre_users) values (?, ?)", (users['usuarios'][i][user]['fechas'][j], user))
                conn.commit()
            for j in range(len(users['usuarios'][i][user]['ips'])):
                cursor.execute("Insert into IPS(ip) values (?)", (users['usuarios'][i][user]['ips'][j],))
                conn.commit()
                cursor.execute("Insert into  USERSTOIPS(ip_user, nombre_users) values (?, ?)",
                               (users['usuarios'][i][user]['ips'][j], user))
                conn.commit()


if __name__ == '__main__':
    main()
