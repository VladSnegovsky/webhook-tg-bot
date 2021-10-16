import os
import psycopg2
from psycopg2 import pool
from contextlib import closing

import config

class DataBase:
    def __init__(self):
        self.pool = psycopg2.pool.SimpleConnectionPool(1, 300, dbname=config.DB_NAME,
                                                       user=config.DB_USER, password=config.DB_PASS,
                                                       host=config.DB_HOST, port=config.DB_PORT)
        if self.pool:
            print("Database Connected!")


    def add_user(self, tg_id):
        connection = self.pool.getconn()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (tg_id, name, age, sex) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
            (tg_id, '', 0, ''))
        connection.commit()
        cursor.close()
        self.pool.putconn(connection)


    def set_name(self, tg_id, name):
        connection = self.pool.getconn()
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET name = %s WHERE tg_id = %s", (name, tg_id))
        connection.commit()
        cursor.close()
        self.pool.putconn(connection)


    def set_age(self, tg_id, age):
        connection = self.pool.getconn()
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET age = %s WHERE tg_id = %s", (age, tg_id))
        connection.commit()
        cursor.close()
        self.pool.putconn(connection)


    def set_sex(self, tg_id, sex):
        connection = self.pool.getconn()
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET sex = %s WHERE tg_id = %s", (sex, tg_id))
        connection.commit()
        cursor.close()
        self.pool.putconn(connection)


    def get_information(self, tg_id):
        connection = self.pool.getconn()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE tg_id = %s", (tg_id,))
        result = cursor.fetchall()
        connection.commit()
        cursor.close()
        self.pool.putconn(connection)
        return result


    def close(self):
        self.pool.closeall()
        print("DataBase closed!")