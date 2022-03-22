import json
import sqlite3


def connect(data):
    conn = sqlite3.connect('BD.db')
    cur = conn.cursor()
    return conn


def save_data(data):
    conn = connect()
    cur = conn.cursor()
    cur.execute('insert into USERS(data) values(%s)', (data,))
    conn.commit()
    conn.close()


def load_data(id):
    conn = connect()
    cur = conn.cursor()
    cur.execute('SELECT * FROM USER WHERE nombre = %s', (id,))
    datos = cur.fetchone()
    conn.close()
    return datos

    legalJSON = json.load(open('legal.json', 'r'))
    usersJSON = json.load(open('users.json', ))
    conn = connect()
    cur = conn.cursor()
    usersdata = json.load(usersJSON)
    # USERS
    cur.execute('create table EMAILS (totals int identity primary key, phising int, ciclados int)')
    cur.execute('create table FECHAS (fecha varchar(255) primary key)')
    cur.execute('create table IPS (ip varchar(255) primary key)')

    cur.execute(
        'create table USERS (nombre varchar(255)  primary key, telefono int(9),contrasena varchar(255),provincia varchar(255),permisos varchar(255),emails varchar(255) FOREIGN KEY REFERENCES EMAILS,fechas varchar(255) FOREIGN KEY REFERENCES USERSTOFECHAS,ips varchar(255))')
    cur.execute(
        'create table USERSTOFECHAS (fecha_user varchar(255) FOREIGN KEY REFERENCES FECHAS,nombre_users varchar(255) FOREIGN KEY REFERENCES USERS, PRIMARY KEY (nombre_users,fecha_user))')
    cur.execute(
        'create table USERSTOIPS (ip_user varchar(255) FOREIGN KEY REFERENCES IPS, nombre_users varchar(255) FOREIGN KEY REFERENCES USERS, PRIMARY KEY (nombre_users,ip_user))')
    # LEGAL
    cur.execute(
        'create table LEGAL (nombre varchar(255) primary key, cookies int,aviso int, proteccion_de_datos int, creacion int)')

    save_data(json.dumps(usersdata))
