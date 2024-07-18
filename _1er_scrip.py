import requests
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from dni_database import DniDatabase

class DniConsultationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Consulta y Registro de DNI")
        self.db = DniDatabase()
        
        self.create_widgets()
        self.layout_widgets()

    def create_widgets(self):
        # Labels and Entries for DNI consultation
        self.lblDni = Label(self.root, text="Número DNI:")
        self.txtDni = Entry(self.root)
        self.txtDni.bind('<Return>', self.consult_dni_event)
        self.btnConsult = Button(self.root, text="Consultar DNI", command=self.consult_dni)
        self.lblMessage = Label(self.root, text="", fg="red")

        # Labels and Entries for registering DNI information
        self.lblApellidoPaterno = Label(self.root, text="Apellido Paterno:")
        self.txtApellidoPaterno = Entry(self.root)
        self.lblApellidoMaterno = Label(self.root, text="Apellido Materno:")
        self.txtApellidoMaterno = Entry(self.root)
        self.lblNombres = Label(self.root, text="Nombres:")
        self.txtNombres = Entry(self.root)
        self.btnSave = Button(self.root, text="Guardar Registro", command=self.save_dni)

        # Treeview to display consulted and registered DNIs
        self.tree = ttk.Treeview(self.root, columns=("DNI", "Apellido Paterno", "Apellido Materno", "Nombres", "Fecha y Hora"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)

        # Buttons for actions
        self.btnExit = Button(self.root, text="Salir", command=self.exit_app)

    def layout_widgets(self):
        # Grid layout for DNI consultation
        self.lblDni.grid(row=0, column=0, padx=10, pady=5, sticky=W)
        self.txtDni.grid(row=0, column=1, padx=10, pady=5)
        self.btnConsult.grid(row=1, column=0, columnspan=2, pady=10)
        self.lblMessage.grid(row=2, column=0, columnspan=2, pady=5)

        # Grid layout for registering DNI information
        self.lblApellidoPaterno.grid(row=3, column=0, padx=10, pady=5, sticky=W)
        self.txtApellidoPaterno.grid(row=3, column=1, padx=10, pady=5)
        self.lblApellidoMaterno.grid(row=4, column=0, padx=10, pady=5, sticky=W)
        self.txtApellidoMaterno.grid(row=4, column=1, padx=10, pady=5)
        self.lblNombres.grid(row=5, column=0, padx=10, pady=5, sticky=W)
        self.txtNombres.grid(row=5, column=1, padx=10, pady=5)
        self.btnSave.grid(row=6, column=0, columnspan=2, pady=10)

        # Grid layout for displaying consulted and registered DNIs
        self.tree.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        # Grid layout for exit button
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
        start_time = datetime.now()

        session = requests.Session()
        token = self.get_token(session)
        if token:
            response = self.fetch_dni_data(session, token, dni)
            if response:
                message, fecha_hora = self.parse_dni_response(response, dni)
                elapsed_time = (datetime.now() - start_time).total_seconds()
                self.lblMessage.config(text=f"Procesado en {elapsed_time:.2f} segundos.")
                if 'exitosamente' in message:
                    self.add_to_table(dni, fecha_hora)
                    self.db.insert_record(dni, self.txtApellidoPaterno.get(), self.txtApellidoMaterno.get(), self.txtNombres.get(), fecha_hora)
                messagebox.showinfo("Consulta DNI", message)
            else:
                messagebox.showwarning("Consulta DNI", "No se pudo obtener la información del DNI.")
        else:
            messagebox.showwarning("Consulta DNI", "No se pudo obtener el token de autenticación.")

        self.btnConsult.config(state=NORMAL)
        self.txtDni.focus()
        self.txtDni.select_range(0, END)

    def clear_entries(self):
        self.txtApellidoPaterno.delete(0, END)
        self.txtApellidoMaterno.delete(0, END)
        self.txtNombres.delete(0, END)
        self.lblMessage.config(text="")

    def get_token(self, session):
        url = "https://eldni.com/pe/buscar-por-dni"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            token = self.extract_between(response.text, 'name="_token" value="', '">')
            return token
        return None

    def fetch_dni_data(self, session, token, dni):
        url = "https://eldni.com/pe/buscar-por-dni"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://eldni.com/pe/buscar-por-dni",
            "Origin": "https://eldni.com"
        }
        data = {
            "_token": token,
            "dni": dni
        }
        response = session.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.text
        return None

    def parse_dni_response(self, response, dni):
        data = re.findall(r'<td>(.*?)</td>', response)
        if len(data) >= 4:
            self.txtApellidoPaterno.insert(0, data[2])
            self.txtApellidoMaterno.insert(0, data[3])
            self.txtNombres.insert(0, data[1])
            return f"Consulta exitosa para el DNI {dni}.", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"No se pudo obtener información para el DNI {dni}.", None

    def add_to_table(self, dni, fecha_hora):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree.insert("", "end", values=(dni, self.txtApellidoPaterno.get(), self.txtApellidoMaterno.get(), self.txtNombres.get(), fecha_hora))

    def save_dni(self):
        dni = self.txtDni.get().strip()
        apellido_paterno = self.txtApellidoPaterno.get().strip()
        apellido_materno = self.txtApellidoMaterno.get().strip()
        nombres = self.txtNombres.get().strip()
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not (dni and apellido_paterno and apellido_materno and nombres):
            messagebox.showerror("Error", "Todos los campos deben estar llenos.")
            return

        if self.db.insert_record(dni, apellido_paterno, apellido_materno, nombres, fecha_hora):
            self.add_to_table(dni, fecha_hora)
            messagebox.showinfo("Guardar DNI", "Registro guardado exitosamente.")
        else:
            messagebox.showwarning("Guardar DNI", "Ya existe un registro con este DNI para la fecha actual.")

    def exit_app(self):
        self.root.destroy()

if __name__ == "__main__":
    root = Tk()
    app = DniConsultationApp(root)
    root.mainloop()
