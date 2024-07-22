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
                                fecha_hora_ingreso TEXT,
                                fecha_hora_salida TEXT
                              )''')
        self.conn.commit()

    def insert_record(self, dni, apellido_paterno, apellido_materno, nombres, fecha_hora_ingreso, fecha_hora_salida=""):
        try:
            # Verificar si ya existe un registro con el mismo DNI y fecha actual para ingreso
            current_date = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("SELECT * FROM dni_records WHERE dni=? AND fecha_hora_ingreso LIKE ?", (dni, f"{current_date}%"))
            existing_record = self.cursor.fetchone()
            if existing_record:
                return False  # Ya existe un registro con este DNI en la fecha actual para ingreso
            
            self.cursor.execute('''INSERT INTO dni_records (dni, apellido_paterno, apellido_materno, nombres, fecha_hora_ingreso, fecha_hora_salida)
                                VALUES (?, ?, ?, ?, ?, ?)''', (dni, apellido_paterno, apellido_materno, nombres, fecha_hora_ingreso, fecha_hora_salida))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_record_salida(self, dni, fecha_hora_salida):
        try:
            # Verificar si ya existe un registro de salida para el mismo DNI y fecha actual
            current_date = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("SELECT * FROM dni_records WHERE dni=? AND fecha_hora_salida LIKE ?", (dni, f"{current_date}%"))
            existing_record = self.cursor.fetchone()
            if existing_record:
                return False  # Ya existe un registro de salida con este DNI en la fecha actual
            
            self.cursor.execute('''UPDATE dni_records SET fecha_hora_salida=? WHERE dni=? AND fecha_hora_ingreso LIKE ?''',
                                (fecha_hora_salida, dni, f"{current_date}%"))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def fetch_all_records(self):
        self.cursor.execute("SELECT * FROM dni_records")
        return self.cursor.fetchall()

    def fetch_records_by_date(self, date):
        self.cursor.execute("SELECT * FROM dni_records WHERE fecha_hora_ingreso LIKE ?", (f"{date}%",))
        return self.cursor.fetchall()

    def fetch_records_by_interval(self, start_date, end_date):
        self.cursor.execute("SELECT * FROM dni_records WHERE fecha_hora_ingreso BETWEEN ? AND ?", (start_date + " 00:00:00", end_date + " 23:59:59"))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

