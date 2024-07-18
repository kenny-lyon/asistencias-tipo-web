from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import Calendar
from dni_database import DniDatabase
from fpdf import FPDF
import openpyxl

class CalendarWindow:
    def __init__(self, root, callback):
        self.root = Toplevel(root)
        self.root.title("Seleccione el Intervalo de Fechas")
        self.callback = callback

        Label(self.root, text="Fecha de Inicio:").pack(pady=5)
        self.cal_inicio = Calendar(self.root, selectmode='day', date_pattern='yyyy-mm-dd', mindate=datetime(2020, 1, 1), maxdate=datetime(2025, 12, 31))
        self.cal_inicio.pack(pady=5)

        Label(self.root, text="Fecha de Fin:").pack(pady=5)
        self.cal_fin = Calendar(self.root, selectmode='day', date_pattern='yyyy-mm-dd', mindate=datetime(2020, 1, 1), maxdate=datetime(2025, 12, 31))
        self.cal_fin.pack(pady=5)

        Button(self.root, text="Seleccionar Intervalo", command=self.select_interval).pack(pady=10)

    def select_interval(self):
        fecha_inicio = self.cal_inicio.get_date()
        fecha_fin = self.cal_fin.get_date()
        self.callback(fecha_inicio, fecha_fin)
        self.root.destroy()

class ReporteDNIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reporte de asistencia de DNI")
        self.db = DniDatabase()
        
        self.create_widgets()
        self.load_today_records()

    def create_widgets(self):
        Button(self.root, text="Buscar por Fecha", command=self.abrir_calendario).grid(row=0, column=0, columnspan=2)
        Label(self.root, text="Registros del Día:").grid(row=1, column=0, columnspan=2)
        
        self.tree = ttk.Treeview(self.root, columns=("DNI", "Apellido Paterno", "Apellido Materno", "Nombres", "Fecha y Hora"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.grid(row=2, column=0, columnspan=2)
        
        Button(self.root, text="Convertir a PDF", command=self.convertir_a_pdf).grid(row=3, column=0, pady=10)
        Button(self.root, text="Convertir a Excel", command=self.convertir_a_excel).grid(row=3, column=1, pady=10)
        Button(self.root, text="Cerrar sesión", command=self.volver_al_login).grid(row=0, column=1, sticky=E)

    def abrir_calendario(self):
        CalendarWindow(self.root, self.load_records_by_interval)

    def load_today_records(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.load_records_by_date(today)

    def load_records_by_date(self, date):
        records = self.db.fetch_records_by_date(date)
        self.update_treeview(records)

    def load_records_by_interval(self, fecha_inicio, fecha_fin):
        records = self.db.fetch_records_by_interval(fecha_inicio, fecha_fin)
        self.update_treeview(records)

    def update_treeview(self, records):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for record in records:
            self.tree.insert("", "end", values=record)

    def convertir_a_pdf(self):
        records = self.db.fetch_all_records()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Reporte de DNI", ln=True, align='C')
        headers = ["DNI", "Apellido Paterno", "Apellido Materno", "Nombres", "Fecha y Hora"]
        for header in headers:
            pdf.cell(40, 10, header, border=1)
        pdf.ln()

        for record in records:
            for item in record:
                pdf.cell(40, 10, str(item), border=1)
            pdf.ln()

        pdf.output("reporte_dni.pdf")
        messagebox.showinfo("Información", "El reporte se ha guardado como PDF")

    def convertir_a_excel(self):
        records = self.db.fetch_all_records()
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Reporte de DNI"

        headers = ["DNI", "Apellido Paterno", "Apellido Materno", "Nombres", "Fecha y Hora"]
        sheet.append(headers)

        for record in records:
            sheet.append(record)

        workbook.save("reporte_dni.xlsx")
        messagebox.showinfo("Información", "El reporte se ha guardado como Excel")

    def volver_al_login(self):
        self.root.destroy()
        restart_login()

if __name__ == "__main__":
    def restart_login():
        root = Tk()
        app = ReporteDNIApp(root)
        root.mainloop()

    restart_login()
