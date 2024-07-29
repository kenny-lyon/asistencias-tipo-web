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
            current_date = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("SELECT * FROM dni_records WHERE dni=? AND fecha_hora_ingreso LIKE ?", (dni, f"{current_date}%"))
            existing_record = self.cursor.fetchone()
            if existing_record:
                return False

            self.cursor.execute('''INSERT INTO dni_records (dni, apellido_paterno, apellido_materno, nombres, fecha_hora_ingreso, fecha_hora_salida)
                                VALUES (?, ?, ?, ?, ?, ?)''', (dni, apellido_paterno, apellido_materno, nombres, fecha_hora_ingreso, fecha_hora_salida))
            self.conn.commit()
            print(f"Inserted record: {dni}, {nombres}, {fecha_hora_ingreso}")
            return True
        except sqlite3.IntegrityError as e:
            print(f"Insert record error: {e}")
            return False

    def update_record_salida(self, dni, fecha_hora_salida):
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("SELECT * FROM dni_records WHERE dni=? AND fecha_hora_salida LIKE ?", (dni, f"{current_date}%"))
            existing_record = self.cursor.fetchone()
            if existing_record:
                return False
            
            self.cursor.execute('''UPDATE dni_records SET fecha_hora_salida=? WHERE dni=? AND fecha_hora_ingreso LIKE ?''',
                                (fecha_hora_salida, dni, f"{current_date}%"))
            self.conn.commit()
            print(f"Updated salida for record: {dni}, {fecha_hora_salida}")
            return True
        except sqlite3.IntegrityError as e:
            print(f"Update salida error: {e}")
            return False

    def fetch_all_names(self):
        self.cursor.execute("SELECT DISTINCT nombres FROM dni_records")
        return [row[0] for row in self.cursor.fetchall()]

    def fetch_records_by_date(self, date):
        self.cursor.execute("SELECT * FROM dni_records WHERE fecha_hora_ingreso LIKE ?", (f"{date}%",))
        records = self.cursor.fetchall()
        print(f"Fetched records by date {date}: {records}")
        return records

    def fetch_records_by_interval(self, start_date, end_date):
        self.cursor.execute("SELECT * FROM dni_records WHERE fecha_hora_ingreso BETWEEN ? AND ?", (start_date + " 00:00:00", end_date + " 23:59:59"))
        records = self.cursor.fetchall()
        print(f"Fetched records by interval {start_date} to {end_date}: {records}")
        return records

    def fetch_records_by_month(self, year, month):
        self.cursor.execute("SELECT dni, nombres, fecha_hora_ingreso, fecha_hora_salida FROM dni_records WHERE strftime('%Y', fecha_hora_ingreso) = ? AND strftime('%m', fecha_hora_ingreso) = ?", (str(year), f'{month:02}'))
        records = self.cursor.fetchall()
        print(f"Fetched records by month {year}-{month}: {records}")
        return records
    
    def fetch_records_by_date_range(self, start_date, end_date):
        self.cursor.execute("SELECT dni, nombres, fecha_hora_ingreso, fecha_hora_salida FROM dni_records WHERE fecha_hora_ingreso BETWEEN ? AND ?", (start_date, end_date))
        records = self.cursor.fetchall()
        print(f"Fetched records by date range {start_date} to {end_date}: {records}")
        return records

    def fetch_all_records(self):
        self.cursor.execute("SELECT * FROM dni_records")
        records = self.cursor.fetchall()
        print(f"Fetched all records: {records}")
        return records

    def close(self):
        self.conn.close()
