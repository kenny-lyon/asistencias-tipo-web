import requests
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import time
from datetime import datetime
from dni_database import DniDatabase

class DniConsultationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Consulta DNI")
        self.db = DniDatabase()
        self.create_widgets()
        self.layout_widgets()

    def create_widgets(self):
        self.lblDni = Label(self.root, text="Número DNI:")
        self.txtDni = Entry(self.root)
        self.txtDni.bind('<Return>', self.consult_dni_event)
        self.btnConsult = Button(self.root, text="Consultar", command=self.consult_dni)
        self.lblMessage = Label(self.root, text="")
        
        self.lblApellidoPaterno = Label(self.root, text="Apellido Paterno:")
        self.txtApellidoPaterno = Entry(self.root)
        self.lblApellidoMaterno = Label(self.root, text="Apellido Materno:")
        self.txtApellidoMaterno = Entry(self.root)
        self.lblNombres = Label(self.root, text="Nombres:")
        self.txtNombres = Entry(self.root)
        self.btnSave = Button(self.root, text="Guardar", command=self.save_dni)

        self.tree = ttk.Treeview(self.root, columns=("DNI", "Apellido Paterno", "Apellido Materno", "Nombres", "Fecha y Hora"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        
        self.btnExit = Button(self.root, text="Regresar", command=self.exit_app)

    def layout_widgets(self):
        self.lblDni.grid(row=0, column=0, padx=10, pady=5, sticky=W)
        self.txtDni.grid(row=0, column=1, padx=10, pady=5)
        self.btnConsult.grid(row=1, column=0, columnspan=2, pady=10)
        self.lblMessage.grid(row=2, column=0, columnspan=2, pady=5)

        self.lblApellidoPaterno.grid(row=3, column=0, padx=10, pady=5, sticky=W)
        self.txtApellidoPaterno.grid(row=3, column=1, padx=10, pady=5)
        self.lblApellidoMaterno.grid(row=4, column=0, padx=10, pady=5, sticky=W)
        self.txtApellidoMaterno.grid(row=4, column=1, padx=10, pady=5)
        self.lblNombres.grid(row=5, column=0, padx=10, pady=5, sticky=W)
        self.txtNombres.grid(row=5, column=1, padx=10, pady=5)
        self.btnSave.grid(row=6, column=0, columnspan=2, pady=10)

        self.tree.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
        self.btnExit.grid(row=8, column=0, columnspan=2, pady=10)

    def consult_dni_event(self, event):
        self.consult_dni()

    def consult_dni(self):
        self.clear_entries()
        dni = self.txtDni.get().strip()
        if not dni:
            self.lblMessage.config(text="Por favor, ingrese un número de DNI.")
            return

        self.btnConsult.config(state=DISABLED)
        start_time = time.time()
        
        token, session = self.get_token()
        if token:
            response = self.fetch_dni_data(session, token, dni)
            if response:
                message, fecha_hora = self.parse_dni_response(response, dni)
                self.lblMessage.config(text=f"Procesado en {time.time() - start_time:.2f} seg.")
                if 'exitosamente' in message:
                    self.add_to_table(dni, fecha_hora)
                    self.db.insert_record(dni, self.txtApellidoPaterno.get(), self.txtApellidoMaterno.get(), self.txtNombres.get(), fecha_hora)
                messagebox.showinfo("Consulta DNI", message)
            else:
                messagebox.showwarning("Consulta DNI", "No se pudo obtener la información del DNI.")
        else:
            messagebox.showwarning("Consulta DNI", "No se pudo obtener el token.")

        self.btnConsult.config(state=NORMAL)
        self.txtDni.focus()
        self.txtDni.select_range(0, END)

    def clear_entries(self):
        self.txtApellidoPaterno.delete(0, END)
        self.txtApellidoMaterno.delete(0, END)
        self.txtNombres.delete(0, END)
        self.lblMessage.config(text="")

    def get_token(self):
        session = requests.Session()
        response = session.get("https://eldni.com/pe/buscar-por-dni")
        if response.status_code == 200:
            token = self.extract_between(response.text, 'name="_token" value="', '">')
            return token, session
        return None, None

    def fetch_dni_data(self, session, token, dni):
        data = {"_token": token, "dni": dni}
        response = session.post("https://eldni.com/pe/buscar-por-dni", data=data)
        if response.status_code == 200:
            return self.extract_between(response.text, '<table class="table table-striped table-scroll">', '</table>')
        return None

    def parse_dni_response(self, response, dni):
        data = re.findall(r'<td>(.*?)</td>', response)
        if len(data) >= 4:
            self.txtApellidoPaterno.insert(0, data[2])
            self.txtApellidoMaterno.insert(0, data[3])
            self.txtNombres.insert(0, data[1])
            return f"Consulta de DNI {dni} realizada exitosamente.", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"No se pudo obtener información para el DNI {dni}.", None

    def add_to_table(self, dni, fecha_hora):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree.insert("", "end", values=(dni, self.txtApellidoPaterno.get(), self.txtApellidoMaterno.get(), self.txtNombres.get(), fecha_hora))

    def save_dni(self):
        dni = self.txtDni.get().strip()
        ap_paterno = self.txtApellidoPaterno.get().strip()
        ap_materno = self.txtApellidoMaterno.get().strip()
        nombres = self.txtNombres.get().strip()
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not (dni and ap_paterno and ap_materno and nombres):
            messagebox.showerror("Error", "Todos los campos deben estar llenos.")
            return

        if self.db.insert_record(dni, ap_paterno, ap_materno, nombres, fecha_hora):
            self.add_to_table(dni, fecha_hora)
            messagebox.showinfo("Guardar DNI", "DNI guardado satisfactoriamente.")
        else:
            messagebox.showwarning("Guardar DNI", "El DNI ya existe para la fecha actual.")

    def exit_app(self):
        self.root.destroy()
        restart_login()

    @staticmethod
    def extract_between(text, start, end):
        return text.split(start)[-1].split(end)[0] if start in text and end in text else ""

if __name__ == "__main__":
    def restart_login():
        root = Tk()
        app = DniConsultationApp(root)
        root.mainloop()

    root = Tk()
    app = DniConsultationApp(root)
    root.mainloop()
