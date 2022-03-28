import sqlite3
from sqlite3 import Error


def create_connection(database):
    try:
        conn = sqlite3.connect(database)
        return conn
    except Error as e:
        print(e)


def main():
    conn = create_connection('bd.db')
    cursor = conn.cursor()
    pepe = "sergio.garcia"
    fecha = "16/8/2021"
    cursor.execute("Select nombre from USERS where nombre = ?", (pepe,))
    cursor.execute("Select fecha_user, nombre_users from USERSTOFECHAS where fecha_user = ? and nombre_users = ?", (fecha, pepe))
    if cursor.fetchall():
        print("Yes")
    else:
        print("No")


if __name__ == '__main__':
    main()
