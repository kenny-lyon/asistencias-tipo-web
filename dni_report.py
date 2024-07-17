from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import Calendar
from dni_database import DniDatabase
from fpdf import FPDF
import openpyxl

class FrmReporteDNI:
    def __init__(self, root):
        self.root = root
      self.root.title("Reporte de asistencia de DNI")  

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

        self.btnPDF = Button(root, text="Convertir a PDF", command=self.convertir_a_pdf)
        self.btnPDF.grid(row=3, column=0, pady=10)

        self.btnExcel = Button(root, text="Convertir a Excel", command=self.convertir_a_excel)
        self.btnExcel.grid(row=3, column=1, pady=10)

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

    def convertir_a_pdf(self):
        records = self.db.fetch_all_records()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Reporte de DNI", ln=True, align='C')

        # Headers
        headers = ["DNI", "Apellido Paterno", "Apellido Materno", "Nombres", "Fecha y Hora"]
        for header in headers:
            pdf.cell(40, 10, header, border=1)
        pdf.ln()

        # Data rows
        for record in records:
            pdf.cell(40, 10, record[1], border=1)
            pdf.cell(40, 10, record[2], border=1)
            pdf.cell(40, 10, record[3], border=1)
            pdf.cell(40, 10, record[4], border=1)
            pdf.cell(40, 10, record[5], border=1)
            pdf.ln()

        pdf.output("reporte_dni.pdf")
        messagebox.showinfo("Éxito", "Los registros se han convertido a PDF correctamente.")

    def convertir_a_excel(self):
        records = self.db.fetch_all_records()
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Reporte de DNI"

        # Headers
        headers = ["DNI", "Apellido Paterno", "Apellido Materno", "Nombres", "Fecha y Hora"]
        sheet.append(headers)

        # Data rows
        for record in records:
            sheet.append([record[1], record[2], record[3], record[4], record[5]])

        workbook.save("reporte_dni.xlsx")
        messagebox.showinfo("Éxito", "Los registros se han convertido a Excel correctamente.")

    def __del__(self):
        self.db.close()

if __name__ == "__main__":
    root = Tk()
    app = FrmReporteDNI(root)
    root.mainloop()
