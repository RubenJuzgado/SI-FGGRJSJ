import json
import sqlite3
from sqlite3 import Error
import pandas as pd


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


def insertar_datos(conn):
    users = json.load(open('users.json'))
    webs = json.load(open('legal.json'))
    cursor = conn.cursor()
    for i in range(len(webs['legal'])):
        for web in webs['legal'][i].keys():
            cursor.execute("Insert into WEBS values (?, ?, ?, ?, ?)", (
                web, webs['legal'][i][web]['cookies'], webs['legal'][i][web]['aviso'],
                webs['legal'][i][web]['proteccion_de_datos'], webs['legal'][i][web]['creacion']))
            conn.commit()
    for i in range(len(users['usuarios'])):
        for user in users['usuarios'][i].keys():
            cursor.execute("Insert into EMAILS values (?, ?, ?, ?)", (
                i, users['usuarios'][i][user]['emails']['total'], users['usuarios'][i][user]['emails']['phishing'],
                users['usuarios'][i][user]['emails']['cliclados']))
            conn.commit()
            cursor.execute("Insert into USERS values (?, ?, ?, ?, ?, ?)", (
                user, users['usuarios'][i][user]['telefono'], users['usuarios'][i][user]['contrasena'],
                users['usuarios'][i][user]['provincia'], users['usuarios'][i][user]['permisos'], i))
            conn.commit()
            for j in range(len(users['usuarios'][i][user]['fechas'])):
                # Voy a comprobar primero si la fecha está ya en la base de datos
                cursor.execute("Select fecha from FECHAS where fecha = ?", (users['usuarios'][i][user]['fechas'][j],))
                if not cursor.fetchall():
                    cursor.execute("Insert into FECHAS(fecha) values (?)", (users['usuarios'][i][user]['fechas'][j],))
                    conn.commit()
                cursor.execute("Insert into  USERSTOFECHAS(fecha_user, nombre_users) values (?, ?)",
                               (users['usuarios'][i][user]['fechas'][j], user))
                conn.commit()
            for j in range(len(users['usuarios'][i][user]['ips'])):
                # Voy a comprobar si ya está guardada la IP
                cursor.execute("Select ip from IPS where ip = ?", (users['usuarios'][i][user]['ips'][j],))
                if not cursor.fetchall():
                    cursor.execute("Insert into IPS(ip) values (?)", (users['usuarios'][i][user]['ips'][j],))
                    conn.commit()
                cursor.execute("Insert into  USERSTOIPS(ip_user, nombre_users) values (?, ?)",
                               (users['usuarios'][i][user]['ips'][j], user))
                conn.commit()


def main():
    conn = create_connection('bd.db')

    #    create_emails = """create table EMAILS (id integer primary key, totals int, phishing int, cliclados int)"""
    #    create_table(conn, create_emails)
    #    create_ips = """create table IPS (id integer primary key autoincrement, ip varchar(255) )"""
    #   create_table(conn, create_ips)
    #  create_fechas = """create table FECHAS (id integer primary key autoincrement, fecha varchar(255))"""
    # create_table(conn, create_fechas)
    # create_users = """create table USERS (nombre varchar(255) primary key, telefono int(9),contrasena varchar(255),provincia varchar(255),permisos varchar(255), emails, FOREIGN KEY (emails) references EMAILS(id))"""
    #    create_table(conn, create_users)
    #   create_userToFechas = """create table USERSTOFECHAS (id integer primary key autoincrement, fecha_user varchar(255), nombre_users varchar(255), FOREIGN KEY (fecha_user) references FECHAS(fecha), FOREIGN KEY (nombre_users) REFERENCES USERS(nombre))"""
    #  create_table(conn, create_userToFechas)
    # create_userToIPS = """create table USERSTOIPS (id integer primary key autoincrement, ip_user varchar(255), nombre_users varchar(255), FOREIGN KEY (ip_user) references IPS(ip), FOREIGN KEY (nombre_users) REFERENCES USERS(nombre))"""
    # create_table(conn, create_userToIPS)
    #   create_legal = """create table WEBS (nombre varchar(255) primary key, cookies int,aviso int, proteccion_de_datos int, creacion int)"""
    #  create_table(conn, create_legal)

    # insertar_datos(conn)

    # Numero muestras

    n_users = pd.read_sql("SELECT USERS.nombre FROM USERS", conn)
    print(n_users.count())
    n_webs = pd.read_sql("SELECT WEBS.nombre FROM WEBS", conn)
    print(n_webs.count())

    # Media y desviacion de fechas de inicio de sesion
    inicios_sesion = pd.read_sql("SELECT nombre_users, COUNT(fecha_user) FROM USERSTOFECHAS GROUP BY nombre_users", conn)
    inicios_sesion = inicios_sesion.rename(columns={"COUNT(fecha_user)":"NLoggin"})
    print("La media de inicios de sesión es: " + str(inicios_sesion['NLoggin'].mean()))
    print("La desviacion estandar de inicios de sesión es: " + str(inicios_sesion['NLoggin'].std()))

    #Media y desviacion de ips
    ips = pd.read_sql("SELECT nombre_users, COUNT(ip_user) FROM USERSTOIPS GROUP BY nombre_users", conn)
    ips = ips.rename(columns={"COUNT(ip_user)": "NIPs"})
    print("La media de IPs es: " + str(ips['NIPs'].mean()))
    print("La desviacion estandar de IPs es: " + str(ips['NIPs'].std()))

    #Media y desviacion de emails recibidos
    emails_recibidos = pd.read_sql("SELECT EMAILS.totals FROM EMAILS", conn)
    emails_recibidos = emails_recibidos.rename(columns={"totals": "NEmails"})
    print("La media de emails recibidos es: " + str(emails_recibidos['NEmails'].mean()))
    print("La desviacion estandar de emails recibidos es: " + str(emails_recibidos['NEmails'].std()))

    #Minimo y maximo valor del total de fechas de inicio de sesion
    print("El numero maximo de inicios de sesion es: " + str(inicios_sesion['NLoggin'].max()))
    print("El numero minimo de inicios de sesion es: " + str(inicios_sesion['NLoggin'].min()))

    # Minimo y maximo valor del total de emails recibidos
    print("El numero maximo de emails recibidos es: " + str(emails_recibidos['NEmails'].max()))
    print("El numero minimo de emails recibidos es: " + str(emails_recibidos['NEmails'].min()))


if __name__ == '__main__':
    main()
