import json
import sqlite3
from hashlib import md5
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


def create_hash(word):
    pass_bytes = word.encode('utf-8')
    pass_hash = md5(pass_bytes)
    digest = pass_hash.hexdigest()
    return digest


def usuariosCriticos():
    conn = create_connection('bd.db')
    dictionary = pd.read_csv("diccionario.csv", names=['passwords'])
    usuarios = pd.read_sql("SELECT * FROM USERS", conn)
    correos = pd.read_sql("SELECT * FROM EMAILS", conn)
    inicios_sesion = pd.read_sql("SELECT nombre_users, COUNT(fecha_user) FROM USERSTOFECHAS GROUP BY nombre_users",
                                 conn)
    inicios_sesion = inicios_sesion.rename(columns={"COUNT(fecha_user)": "NLoggin"})
    usuarios_correos = pd.merge(usuarios, correos, left_on='emails', right_on='id')
    usuario_contrasena = pd.DataFrame()
    usuario_contrasena['nombre'] = usuarios['nombre']
    usuario_contrasena['contrasena'] = usuarios['contrasena']
    usuario_contrasena_mal = pd.DataFrame()
    usuario_contrasena_bien = pd.DataFrame()
    usuario_contrasena = usuario_contrasena.assign(contrasenabien=1)
    inicios_sesion = inicios_sesion.assign(contrasenabien=1)
    for i in range(usuario_contrasena.shape[0]):
         hashh = usuario_contrasena.at[i, 'contrasena']
         for test_word in dictionary["passwords"]:
             crackeada = 0
             if str(create_hash(test_word)) == str(hashh):
                 usuario_contrasena.loc[i, 'contrasenabien'] = 0
                 inicios_sesion.loc[i, 'contrasenabien'] = 0
                 crackeada = 1
                 break

    usuario_contrasena_mal = usuario_contrasena.loc[(usuario_contrasena['contrasenabien'] == 0)]
    usuario_contrasena_bien = usuario_contrasena.loc[(usuario_contrasena['contrasenabien'] == 1)]

    porcentajes_clickados = pd.DataFrame()
    porcentajes_clickados['porcentaje'] = (usuarios_correos['cliclados'] * 100) / usuarios_correos['totals']
    porcentajes_clickados['nombreu'] = usuarios_correos['nombre']
    porcentajes_clickados = porcentajes_clickados.sort_values(by='porcentaje', ascending=False)
    apartado1 = pd.merge(porcentajes_clickados, usuario_contrasena, left_on='nombreu', right_on='nombre')
    apartado1 = apartado1.where(apartado1['contrasenabien'] == 0)
    apartado1 = apartado1.dropna()
    conn.close()

    return apartado1

def websCriticas():
    conn = create_connection('bd.db')
    paginas_desactualizadas = pd.DataFrame()
    paginas = pd.read_sql("SELECT * FROM WEBS", conn)
    paginas_desactualizadas = paginas
    paginas_desactualizadas['total'] = paginas_desactualizadas['cookies'] + paginas_desactualizadas['aviso'] + \
                                       paginas_desactualizadas['proteccion_de_datos']
    paginas_desactualizadas = paginas_desactualizadas.sort_values(by='total', ascending=False)
    conn.close()
    return paginas_desactualizadas

def mas50Clickados():
    conn = create_connection('bd.db')
    usuarios = pd.read_sql("SELECT * FROM USERS", conn)
    correos = pd.read_sql("SELECT * FROM EMAILS", conn)
    usuarios_correos = pd.merge(usuarios, correos, left_on='emails', right_on='id')
    usuarios_correos['porcentajeSpamClick'] = usuarios_correos['cliclados'] * 100 / usuarios_correos['phishing']
    usuarios_mas50 = usuarios_correos.where(usuarios_correos['porcentajeSpamClick'] > 50)
    usuarios_mas50 = usuarios_mas50.dropna()
    usuarios_mas50 = usuarios_mas50.sort_values(by='porcentajeSpamClick', ascending=False)

    return usuarios_mas50


def menos50Clickados():
    conn = create_connection('bd.db')
    usuarios = pd.read_sql("SELECT * FROM USERS", conn)
    correos = pd.read_sql("SELECT * FROM EMAILS", conn)
    usuarios_correos = pd.merge(usuarios, correos, left_on='emails', right_on='id')
    usuarios_correos['porcentajeSpamClick'] = usuarios_correos['cliclados'] * 100 / usuarios_correos['phishing']
    usuarios_menos50 = usuarios_correos.where(usuarios_correos['porcentajeSpamClick'] <= 50)
    usuarios_menos50 = usuarios_menos50.dropna()
    usuarios_menos50 = usuarios_menos50.sort_values(by='porcentajeSpamClick', ascending=False)
    return usuarios_menos50



def main():
    conn = create_connection('bd.db')
    dictionary = pd.read_csv("diccionario.csv", names=['passwords'])
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
    n_webs = pd.read_sql("SELECT WEBS.nombre FROM WEBS", conn)

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

    # Ejercicio 4
    # Apartado 1

    #Checkpasswords
    usuario_contrasena = pd.DataFrame()
    usuario_contrasena['nombre'] = usuarios['nombre']
    usuario_contrasena['contrasena'] = usuarios['contrasena']
    usuario_contrasena_mal = pd.DataFrame()
    usuario_contrasena_bien = pd.DataFrame()
    usuario_contrasena = usuario_contrasena.assign(contrasenabien=1)
    inicios_sesion = inicios_sesion.assign(contrasenabien=1)
    for i in range(usuario_contrasena.shape[0]):
         hashh = usuario_contrasena.at[i, 'contrasena']
         for test_word in dictionary["passwords"]:
             crackeada = 0
             if str(create_hash(test_word)) == str(hashh):
                 print("Found Matched Password:" + str(test_word) + "for user" + str(usuario_contrasena.at[i, 'nombre']))
                 usuario_contrasena.loc[i, 'contrasenabien'] = 0
                 inicios_sesion.loc[i, 'contrasenabien'] = 0
                 crackeada = 1
                 break

    usuario_contrasena_mal = usuario_contrasena.loc[(usuario_contrasena['contrasenabien'] == 0)]
    usuario_contrasena_bien = usuario_contrasena.loc[(usuario_contrasena['contrasenabien'] == 1)]

    porcentajes_clickados = pd.DataFrame()
    porcentajes_clickados['porcentaje'] = (usuarios_correos['cliclados'] * 100) / usuarios_correos['totals']
    porcentajes_clickados['nombreu'] = usuarios_correos['nombre']
    porcentajes_clickados = porcentajes_clickados.sort_values(by='porcentaje', ascending=False)
    apartado1 = pd.merge(porcentajes_clickados, usuario_contrasena, left_on='nombreu', right_on='nombre')
    apartado1 = apartado1.where(apartado1['contrasenabien'] == 0)
    apartado1 = apartado1.dropna()
    apartado1 = apartado1.head(10)
    porplot = apartado1.plot(x='nombreu', y='porcentaje', kind='bar')
    plt.subplots_adjust(bottom=0.26)

    # Apartado 2
    paginas_desactualizadas = pd.DataFrame()
    paginas = pd.read_sql("SELECT * FROM WEBS", conn)
    paginas_desactualizadas = paginas
    paginas_desactualizadas['total'] = paginas_desactualizadas['cookies'] + paginas_desactualizadas['aviso'] + \
                                       paginas_desactualizadas['proteccion_de_datos']
    paginas_desactualizadas = paginas_desactuesactualizadas = paginas_desactualizadas.tail(5)
    paginas_desactualizadas = paginas_desactualizadas.sort_values(by='creacion')
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
    # Apartado 3
    inicios_sesion_mal = inicios_sesion.loc[(inicios_sesion['contrasenabien'] == 0)]
    inicios_sesion_bien = inicios_sesion.loc[(inicios_sesion['contrasenabien'] == 1)]
    ejey = (inicios_sesion_mal['NLoggin'].mean(), inicios_sesion_bien['NLoggin'].mean())
    mediamal = inicios_sesion_mal['NLoggin'].mean()
    mediabien = inicios_sesion_bien['NLoggin'].mean()
    mediascondata = {'media': [mediamal, mediabien]}
    mediascon = pd.DataFrame(mediascondata)
    mediascon = mediascon.assign(nombre=["Comprometidas", "No comprometidas"])
    mediasconplot = mediascon.plot(x='nombre', y='media', kind='bar')
    plt.subplots_adjust(bottom=0.3)
    plt.show()

    # Apartado 4
    paginasAct = paginas
    paginasAct['total'] = paginasAct['cookies'] + paginasAct['aviso'] + paginasAct['proteccion_de_datos']
    paginasDes = paginasAct
    paginasAct = pd.DataFrame.where(paginasAct, paginasAct['total'] == 3)
    paginasDes = pd.DataFrame.where(paginasDes, paginasDes['total'] != 3)
    paginasAct = paginasAct.sort_values(by='creacion')
    paginasDes = paginasDes.sort_values(by='creacion')
    paginasAct = paginasAct.head(6)
    pagActplot = paginasAct.plot(x='nombre', y='creacion', kind='bar')
    plt.ylim(2000, 2023)
    plt.subplots_adjust(bottom=0.26)
    plt.savefig("porACTplot.png", dpi=150)

    paginasDes = paginasDes.head(14)
    pagDesplot = paginasDes.plot(x='nombre', y='creacion', kind='bar')
    plt.ylim(2000, 2023)

    plt.subplots_adjust(bottom=0.32)
    plt.savefig("porDESplot.png", dpi=150)
    plt.show()

    #######

    # Apartado 5
    # PIE CHART EXTRA
    labels = 'No comprometidas', 'Comprometidas'
    sizes = [usuario_contrasena_bien.shape[0], usuario_contrasena_mal.shape[0]]
    plt.figure(figsize=(5, 5))
    plt.pie(sizes, labels=labels, autopct='%.2f%%', shadow=True)
    plt.savefig("piepassbienplot.png", dpi=150)

    # BARRAS PLOT

    usuario_contrasena_count = usuario_contrasena[["contrasenabien"]].apply(pd.value_counts)
    usuario_contrasena_count.plot(kind="bar")
    scale_factor = 0.9
    xmin, xmax = plt.xlim()
    ymin, ymax = plt.ylim()
    plt.xlim(xmin * scale_factor, xmax * scale_factor)
    plt.ylim(ymin * scale_factor, ymax * scale_factor)
    plt.show()


if __name__ == '__main__':
    main()
