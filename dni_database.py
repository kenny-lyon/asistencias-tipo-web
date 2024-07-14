import sqlite3

class DniDatabase:
    def __init__(self, db_name="dni_records.db"):
        self.connection = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS registros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dni TEXT NOT NULL,
                    apellido_paterno TEXT NOT NULL,
                    apellido_materno TEXT NOT NULL,
                    nombres TEXT NOT NULL,
                    fecha_hora TEXT NOT NULL
                )
                """
            )

    def insert_record(self, dni, apellido_paterno, apellido_materno, nombres, fecha_hora):
        with self.connection:
            if not self.record_exists(dni, fecha_hora):
                self.connection.execute(
                    """
                    INSERT INTO registros (dni, apellido_paterno, apellido_materno, nombres, fecha_hora)
                    VALUES (?, ?, ?, ?, ?)
                    """, 
                    (dni, apellido_paterno, apellido_materno, nombres, fecha_hora)
                )
                return True
            else:
                return False

    def record_exists(self, dni, fecha_hora):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT 1 FROM registros
            WHERE dni = ? AND DATE(fecha_hora) = DATE(?)
            """, 
            (dni, fecha_hora)
        )
        return cursor.fetchone() is not None

    def fetch_all_records(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM registros")
        return cursor.fetchall()

    def fetch_records_by_date(self, date):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT * FROM registros
            WHERE DATE(fecha_hora) = ?
            ORDER BY TIME(fecha_hora) ASC
            """, 
            (date,)
        )
        return cursor.fetchall()

    def close(self):
        self.connection.close()
