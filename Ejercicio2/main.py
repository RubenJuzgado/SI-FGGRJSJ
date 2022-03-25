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
    create_emails = """create table EMAILS (id integer primary key autoincrement, totals int, phising int, ciclados int)"""
    create_table(conn, create_emails)
    create_ips = """create table IPS (id integer primary key autoincrement, ip varchar(255))"""
    create_table(conn, create_ips)
    create_fechas = """create table FECHAS (id integer primary key autoincrement, fecha varchar(255))"""
    create_table(conn, create_fechas)
    create_users = """create table USERS (nombre varchar(255) primary key, telefono int(9),contrasena varchar(255),provincia varchar(255),permisos varchar(255), emails integer, fechas integer, ips integer, FOREIGN KEY (emails) references EMAILS(id), FOREIGN KEY (fechas) references FECHAS(id), FOREIGN KEY (ips) references IPS(id))"""
    create_table(conn, create_users)
    """
    cur.execute(
        'create table USERS (nombre varchar(255) primary key, telefono int(9),contrasena varchar(255),provincia varchar(255),permisos varchar(255),emails varchar(255) FOREIGN KEY REFERENCES EMAILS, ips varchar(255))')
    cur.execute(
        'create table USERSTOFECHAS (fecha_user varchar(255) FOREIGN KEY REFERENCES FECHAS,nombre_users varchar(255) FOREIGN KEY REFERENCES USERS, PRIMARY KEY (nombre_users,fecha_user))')
    cur.execute(
        'create table USERSTOIPS (ip_user varchar(255) FOREIGN KEY REFERENCES IPS,nombre_users varchar(255) FOREIGN KEY REFERENCES USERS, PRIMARY KEY (nombre_users,ip_user))')
    # LEGAL
    cur.execute(
        'create table LEGAL (nombre varchar(255) primary key, cookies int,aviso int, proteccion_de_datos int, creacion int)')

    # save_data(json.dumps(usersdata))
    """


if __name__ == '__main__':
    main()
