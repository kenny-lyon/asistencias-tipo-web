import sqlite3
from datetime import datetime

class DniDatabase:
    def __init__(self):
        # Inicializa la conexión a la base de datos
        self.conn = sqlite3.connect('dni_database.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Crea la tabla si no existe
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros (
                dni TEXT PRIMARY KEY,
                apellido_paterno TEXT,
                apellido_materno TEXT,
                nombres TEXT,
                fecha_hora TEXT
            )
        ''')
        self.conn.commit()

    def insert_record(self, dni, apellido_paterno, apellido_materno, nombres, fecha_hora):
        try:
            self.cursor.execute('''
                INSERT INTO registros (dni, apellido_paterno, apellido_materno, nombres, fecha_hora)
                VALUES (?, ?, ?, ?, ?)
            ''', (dni, apellido_paterno, apellido_materno, nombres, fecha_hora))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def record_exists_today(self, dni):
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute('''
            SELECT * FROM registros
            WHERE dni = ? AND fecha_hora LIKE ?
        ''', (dni, f'{today}%'))
        return self.cursor.fetchone() is not None

    def fetch_records_by_date(self, date):
        self.cursor.execute('''
            SELECT * FROM registros
            WHERE fecha_hora LIKE ?
        ''', (f'{date}%',))
        return self.cursor.fetchall()

    def fetch_records_by_interval(self, start_date, end_date):
        self.cursor.execute('''
            SELECT * FROM registros
            WHERE date(fecha_hora) BETWEEN ? AND ?
        ''', (start_date, end_date))
        return self.cursor.fetchall()

    def fetch_all_records(self):
        self.cursor.execute('''
            SELECT * FROM registros
        ''')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()


