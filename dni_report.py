from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import Calendar, DateEntry
from dni_database import DniDatabase

class FrmReporteDNI:
    def __init__(self, root):
        self.root = root
        self.root.title("Reporte de DNI")

        self.db = DniDatabase()

        self.btnBuscar = Button(root, text="Buscar por Fecha", command=self.abrir_calendario)
        self.btnBuscar.grid(row=0, column=0, columnspan=2)

        self.lblRegistrosHoy = Label(root, text="Registros del Día:")
        self.lblRegistrosHoy.grid(row=1, column=0, columnspan=2)

        self.tree = ttk.Treeview(root, columns=("DNI", "Apellido Paterno", "Apellido Materno", "Nombres", "Fecha y Hora"), show='headings')
        self.tree.heading("DNI", text="DNI")
        self.tree.heading("Apellido Paterno", text="Apellido Paterno")
        self.tree.heading("Apellido Materno", text="Apellido Materno")
        self.tree.heading("Nombres", text="Nombres")
        self.tree.heading("Fecha y Hora", text="Fecha y Hora")
        self.tree.grid(row=2, column=0, columnspan=2)

        self.load_today_records()

    def abrir_calendario(self):
        self.cal_window = Toplevel(self.root)
        self.cal_window.title("Seleccione la Fecha")

        today = datetime.now().strftime("%Y-%m-%d")

        self.cal = Calendar(self.cal_window, selectmode='day', date_pattern='yyyy-mm-dd', mindate=datetime(2020, 1, 1), maxdate=datetime(2025, 12, 31))
        self.cal.pack(pady=10)

        # Destacar la fecha de hoy
        self.cal.calevent_create(datetime.now(), 'Hoy', 'today')

        self.btnSeleccionar = Button(self.cal_window, text="Seleccionar Fecha", command=self.seleccionar_fecha)
        self.btnSeleccionar.pack(pady=10)

    def seleccionar_fecha(self):
        date = self.cal.get_date()
        self.load_records_by_date(date)
        self.cal_window.destroy()

    def load_today_records(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.load_records_by_date(today)

    def load_records_by_date(self, date):
        records = self.db.fetch_records_by_date(date)
        for record in self.tree.get_children():
            self.tree.delete(record)
        for record in records:
            self.tree.insert("", "end", values=(record[1], record[2], record[3], record[4], record[5]))

    def __del__(self):
        self.db.close()

if __name__ == "__main__":
    root = Tk()
    app = FrmReporteDNI(root)
    root.mainloop()
