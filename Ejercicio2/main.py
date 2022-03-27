import json
import sqlite3
from sqlite3 import Error

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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

    # create_emails = """create table EMAILS (id integer primary key, totals int, phishing int, cliclados int)"""
    # create_table(conn, create_emails)
    # create_ips = """create table IPS (id integer primary key autoincrement, ip varchar(255) )"""
    # create_table(conn, create_ips)
    # create_fechas = """create table FECHAS (id integer primary key autoincrement, fecha varchar(255))"""
    # create_table(conn, create_fechas)
    # create_users = """create table USERS (nombre varchar(255) primary key, telefono int(9),contrasena varchar(255),provincia varchar(255),permisos varchar(255), emails, FOREIGN KEY (emails) references EMAILS(id))"""
    # create_table(conn, create_users)
    # create_userToFechas = """create table USERSTOFECHAS (id integer primary key autoincrement, fecha_user varchar(255), nombre_users varchar(255), FOREIGN KEY (fecha_user) references FECHAS(fecha), FOREIGN KEY (nombre_users) REFERENCES USERS(nombre))"""
    # create_table(conn, create_userToFechas)
    # create_userToIPS = """create table USERSTOIPS (id integer primary key autoincrement, ip_user varchar(255), nombre_users varchar(255), FOREIGN KEY (ip_user) references IPS(ip), FOREIGN KEY (nombre_users) REFERENCES USERS(nombre))"""
    # create_table(conn, create_userToIPS)
    # create_legal = """create table WEBS (nombre varchar(255) primary key, cookies int,aviso int, proteccion_de_datos int, creacion int)"""
    # create_table(conn, create_legal)

    # insertar_datos(conn)
    # Numero muestras

    n_users = pd.read_sql("SELECT USERS.nombre FROM USERS", conn)
    print(n_users.count())
    n_webs = pd.read_sql("SELECT WEBS.nombre FROM WEBS", conn)
    print(n_webs.count())

    # Media y desviacion de fechas de inicio de sesion
    inicios_sesion = pd.read_sql("SELECT nombre_users, COUNT(fecha_user) FROM USERSTOFECHAS GROUP BY nombre_users",
                                 conn)
    inicios_sesion = inicios_sesion.rename(columns={"COUNT(fecha_user)": "NLoggin"})
    print("La media de inicios de sesión es: " + str(inicios_sesion['NLoggin'].mean()))
    print("La desviacion estandar de inicios de sesión es: " + str(inicios_sesion['NLoggin'].std()))

    # Media y desviacion de ips
    ips = pd.read_sql("SELECT nombre_users, COUNT(ip_user) FROM USERSTOIPS GROUP BY nombre_users", conn)
    ips = ips.rename(columns={"COUNT(ip_user)": "NIPs"})
    print("La media de IPs es: " + str(ips['NIPs'].mean()))
    print("La desviacion estandar de IPs es: " + str(ips['NIPs'].std()))

    # Media y desviacion de emails recibidos
    emails_recibidos = pd.read_sql("SELECT EMAILS.totals FROM EMAILS", conn)
    emails_recibidos = emails_recibidos.rename(columns={"totals": "NEmails"})
    print("La media de emails recibidos es: " + str(emails_recibidos['NEmails'].mean()))
    print("La desviacion estandar de emails recibidos es: " + str(emails_recibidos['NEmails'].std()))

    # Minimo y maximo valor del total de fechas de inicio de sesion
    print("El numero maximo de inicios de sesion es: " + str(inicios_sesion['NLoggin'].max()))
    print("El numero minimo de inicios de sesion es: " + str(inicios_sesion['NLoggin'].min()))

    # Minimo y maximo valor del total de emails recibidos
    print("El numero maximo de emails recibidos es: " + str(emails_recibidos['NEmails'].max()))
    print("El numero minimo de emails recibidos es: " + str(emails_recibidos['NEmails'].min()))

    # EJERCICIO 3

    usuarios = pd.read_sql("SELECT * FROM USERS", conn)
    correos = pd.read_sql("SELECT * FROM EMAILS", conn)
    usuarios_correos = pd.merge(usuarios, correos, left_on='emails', right_on='id')
    muchos_correos = pd.DataFrame.where(usuarios_correos, usuarios_correos['totals'] >= 200)
    pocos_correos = pd.DataFrame.where(usuarios_correos, usuarios_correos['totals'] < 200)
    privilegiados = pd.DataFrame.where(usuarios_correos, usuarios_correos['permisos'] == '1')
    no_privilegiados = pd.DataFrame.where(usuarios_correos, usuarios_correos['permisos'] == '0')
    # Numero de observaciones
    print("Numero de observaciones de usuarios con menos de 200 correos: " + str(pocos_correos['phishing'].count()))
    print("Numero de observaciones de usuarios con 200 correos o más: " + str(muchos_correos['phishing'].count()))
    print("Numero de observaciones de usuarios no privilegiados: " + str(no_privilegiados['phishing'].count()))
    print("Numero de observaciones de usuarios administradores: " + str(privilegiados['phishing'].count()))

    # Numero de missing
    print("Numero de missing de usuarios con menos de 200 correos: " + str(pocos_correos['phishing'].isnull().sum()))
    print("Numero de missing de usuarios con 200 correos o más: " + str(muchos_correos['phishing'].isnull().sum()))
    print("Numero de missing de usuarios no privilegiados: " + str(no_privilegiados['phishing'].isnull().sum()))
    print("Numero de missing de usuarios administradores: " + str(privilegiados['phishing'].isnull().sum()))

    # Media
    print("Media correos phishing de usuarios con menos de 200 correos: " + str(pocos_correos['phishing'].mean()))
    print("Media correos phishing de usuarios con 200 correos o más: " + str(muchos_correos['phishing'].mean()))
    print("Media correos phishing de usuarios no privilegiados: " + str(no_privilegiados['phishing'].mean()))
    print("Media correos phishing de usuarios administradores: " + str(privilegiados['phishing'].mean()))

    # Mediana
    print("Mediana correos phishing de usuarios con menos de 200 correos: " + str(pocos_correos['phishing'].median()))
    print("Mediana correos phishing de usuarios con 200 correos o más: " + str(muchos_correos['phishing'].median()))
    print("Mediana correos phishing de usuarios no privilegiados: " + str(no_privilegiados['phishing'].median()))
    print("Mediana correos phishing de usuarios administradores: " + str(privilegiados['phishing'].median()))

    # Varianza
    print("Varianza correos phishing de usuarios con menos de 200 correos: " + str(pocos_correos['phishing'].var()))
    print("Varianza correos phishing de usuarios con 200 correos o más: " + str(muchos_correos['phishing'].var()))
    print("Varianza correos phishing de usuarios no privilegiados: " + str(no_privilegiados['phishing'].var()))
    print("Varianza correos phishing de usuarios administradores: " + str(privilegiados['phishing'].var()))

    # Minimo
    print("Minimo correos phishing de usuarios con menos de 200 correos: " + str(pocos_correos['phishing'].min()))
    print("Minimo correos phishing de usuarios con 200 correos o más: " + str(muchos_correos['phishing'].min()))
    print("Minimo correos phishing de usuarios no privilegiados: " + str(no_privilegiados['phishing'].min()))
    print("Minimo correos phishing de usuarios administradores: " + str(privilegiados['phishing'].min()))

    # Maximo
    print("Maximo correos phishing de usuarios con menos de 200 correos: " + str(pocos_correos['phishing'].max()))
    print("Maximo correos phishing de usuarios con 200 correos o más: " + str(muchos_correos['phishing'].max()))
    print("Maximo correos phishing de usuarios no privilegiados: " + str(no_privilegiados['phishing'].max()))
    print("Maximo correos phishing de usuarios administradores: " + str(privilegiados['phishing'].max()))

    porcentajes_clickados = pd.DataFrame()
    porcentajes_clickados
    porcentajes_clickados['porcentaje'] = (usuarios_correos['cliclados'] * 100) / usuarios_correos['totals']
    porcentajes_clickados['nombreu'] = usuarios_correos['nombre']
    print(porcentajes_clickados)
    porcentajes_clickados = porcentajes_clickados.sort_values(by='porcentaje', ascending=False)
    print(porcentajes_clickados.head(10))
    porplot = porcentajes_clickados.head(10).plot(x='nombreu', y='porcentaje', kind='bar')
    plt.subplots_adjust(bottom=0.26)
    plt.savefig("porplot.png", dpi=150)

    paginas_desactualizadas = pd.DataFrame()
    paginas = pd.read_sql("SELECT * FROM WEBS", conn)
    paginas_desactualizadas = paginas
    paginas_desactualizadas['total'] = paginas_desactualizadas['cookies'] + paginas_desactualizadas['aviso'] + \
                                       paginas_desactualizadas['proteccion_de_datos']
    paginas_desactualizadas = paginas_desactualizadas.sort_values(by='total', ascending=False)
    paginas_desactualizadas = paginas_desactualizadas.tail(5)
    paginas_desactualizadas = paginas_desactualizadas.sort_values(by='creacion')
    print(paginas_desactualizadas)
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    label = paginas_desactualizadas["nombre"]
    x = np.arange(len(label))
    width = 0.2
    rect1 = ax.bar(x - width, paginas_desactualizadas['cookies'], width=width, label="Cookies")
    rect2 = ax.bar(x, paginas_desactualizadas['aviso'], width=width, label="Aviso", edgecolor="black")
    rects2 = ax.bar(x + width, paginas_desactualizadas['proteccion_de_datos'], width=width, label="Proteccion_de_Datos",
                    edgecolor="black")
    ax.set_ylabel("Total_Desactualizadas", fontsize=25, labelpad=20)
    ax.set_xlabel("Webs", fontsize=25, labelpad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(label)
    ax.legend(title="Politicas Actualizadas", fontsize=16, title_fontsize=20, bbox_to_anchor=(1.02, 0.7))
    ax.tick_params(axis="x", which="both", labelrotation=90, labelsize=15)
    ax.tick_params(axis="y", which="both", labelsize=0.1)
    plt.subplots_adjust(bottom=0.4, right=0.6)
    plt.savefig("desactplot.png", dpi=150)

    ####
    #usuarios_conexiones = pd.DataFrame()
    #usuarios_conexiones['nombreuser'] = pd.read_sql("SELECT nombre_users, ip_user FROM USERSTOIPS GROUP BY (nombre_users)", conn)
    ######hay  hacerlo

    #########
    paginasAct = paginas
    paginasAct['total'] = paginasAct['cookies'] + paginasAct['aviso'] + paginasAct['proteccion_de_datos']
    paginasDes = paginasAct
    paginasAct = pd.DataFrame.where(paginasAct, paginasAct['total'] == 3)
    paginasDes = pd.DataFrame.where(paginasDes, paginasDes['total'] != 3)
    paginasAct = paginasAct.sort_values(by='creacion')
    paginasDes = paginasDes.sort_values(by='creacion')
    print(paginasAct)
    print(paginasDes)

    pagActplot = paginasAct.plot(x='nombre', y='creacion', kind='bar')
    plt.ylim(2000, 2023)
    plt.savefig("porACTplot.png", dpi=150)
    pagDesplot = paginasDes.plot(x='nombre', y='creacion', kind='bar')
    plt.ylim(2000, 2023)

    plt.subplots_adjust(bottom=0.26)
    plt.savefig("porDESplot.png", dpi=150)
    plt.show()


if __name__ == '__main__':
    main()
