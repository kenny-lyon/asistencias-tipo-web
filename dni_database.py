# dni_database.py

import sqlite3
from datetime import datetime

class DniDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('dni_records.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS dni_records (
                                id INTEGER PRIMARY KEY,
                                dni TEXT,
                                apellido_paterno TEXT,
                                apellido_materno TEXT,
                                nombres TEXT,
                                fecha_hora TEXT
                              )''')
        self.conn.commit()

    def insert_record(self, dni, apellido_paterno, apellido_materno, nombres, fecha_hora):
        try:
            self.cursor.execute('''INSERT INTO dni_records (dni, apellido_paterno, apellido_materno, nombres, fecha_hora)
                                VALUES (?, ?, ?, ?, ?)''', (dni, apellido_paterno, apellido_materno, nombres, fecha_hora))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error al insertar registro: {e}")
            return False

    def fetch_all_records(self):
        self.cursor.execute("SELECT * FROM dni_records")
        return self.cursor.fetchall()

    def fetch_records_by_date(self, date):
        self.cursor.execute("SELECT * FROM dni_records WHERE fecha_hora LIKE ?", (f"{date}%",))
        return self.cursor.fetchall()

    def fetch_records_by_interval(self, start_date, end_date):
        self.cursor.execute("SELECT * FROM dni_records WHERE fecha_hora BETWEEN ? AND ?", (start_date + " 00:00:00", end_date + " 23:59:59"))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

