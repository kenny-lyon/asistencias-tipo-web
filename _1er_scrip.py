import requests
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import time
import re
from datetime import datetime
from dni_database import DniDatabase

class FrmConsultaDNI:
    def __init__(self, root, restart_callback):
        self.root = root
        self.root.title("Consulta DNI")
        self.restart_callback = restart_callback

        # Initialize database
        self.db = DniDatabase()

        # Define styles
        self.define_styles()

        # UI Elements
        self.create_widgets()
        self.layout_widgets()

    def define_styles(self):
        self.bg_color = "#e0f7fa"
        self.label_color = "#00695c"
        self.entry_bg_color = "#ffffff"
        self.btn_color = "#00796b"
        self.btn_fg_color = "#ffffff"
        self.msg_color = "#d32f2f"

        self.root.configure(bg=self.bg_color)

    def create_widgets(self):
        self.lblNumeroDNI = Label(self.root, text="Número DNI:", bg=self.bg_color, fg=self.label_color, font=("Arial", 12, "bold"))
        self.txtNumeroDNI = Entry(self.root, bg=self.entry_bg_color, font=("Arial", 12))
        self.txtNumeroDNI.bind('<Return>', self.consultar_dni_event)  # Bind Enter key to consultar_dni_event

        self.btnConsultar = Button(self.root, text="Consultar DNI", bg=self.btn_color, fg=self.btn_fg_color, font=("Arial", 12, "bold"), command=self.consultar_dni)

        self.lblApellidoPaterno = Label(self.root, text="Apellido Paterno:", bg=self.bg_color, fg=self.label_color, font=("Arial", 12, "bold"))
        self.txtApellidoPaterno = Entry(self.root, bg=self.entry_bg_color, font=("Arial", 12))

        self.lblApellidoMaterno = Label(self.root, text="Apellido Materno:", bg=self.bg_color, fg=self.label_color, font=("Arial", 12, "bold"))
        self.txtApellidoMaterno = Entry(self.root, bg=self.entry_bg_color, font=("Arial", 12))

        self.lblNombres = Label(self.root, text="Nombres:", bg=self.bg_color, fg=self.label_color, font=("Arial", 12, "bold"))
        self.txtNombres = Entry(self.root, bg=self.entry_bg_color, font=("Arial", 12))

        self.btnGuardar = Button(self.root, text="Guardar", bg=self.btn_color, fg=self.btn_fg_color, font=("Arial", 12, "bold"), command=self.guardar_dni)

        self.tree = ttk.Treeview(self.root, columns=("DNI", "Apellido Paterno", "Apellido Materno", "Nombres", "Fecha y Hora"), show='headings')
        self.tree.heading("DNI", text="DNI")
        self.tree.heading("Apellido Paterno", text="Apellido Paterno")
        self.tree.heading("Apellido Materno", text="Apellido Materno")
        self.tree.heading("Nombres", text="Nombres")
        self.tree.heading("Fecha y Hora", text="Fecha y Hora")

        self.lblMensaje = Label(self.root, text="", bg=self.bg_color, fg=self.msg_color, font=("Arial", 12, "bold"))

        self.btnExit = Button(self.root, text="REGRESAR", bg=self.btn_color, fg=self.btn_fg_color, font=("Arial", 12, "bold"), command=self.salir)

    def layout_widgets(self):
        self.lblNumeroDNI.grid(row=0, column=0, padx=10, pady=5, sticky=W)
        self.txtNumeroDNI.grid(row=0, column=0, padx=10, pady=5, sticky=E)

        self.btnConsultar.grid(row=1, column=0, columnspan=2, pady=10)

        self.lblApellidoPaterno.grid(row=2, column=0, padx=10, pady=5, sticky=W)
        self.txtApellidoPaterno.grid(row=2, column=0, padx=10, pady=5, sticky=E)

        self.lblApellidoMaterno.grid(row=3, column=0, padx=10, pady=5, sticky=W)
        self.txtApellidoMaterno.grid(row=3, column=0, padx=10, pady=5, sticky=E)

        self.lblNombres.grid(row=4, column=0, padx=10, pady=5, sticky=W)
        self.txtNombres.grid(row=4, column=0, padx=10, pady=5, sticky=E)

        self.btnGuardar.grid(row=5, column=0, columnspan=2, pady=10)

        self.tree.grid(row=6, column=0, columnspan=2, pady=10, padx=10)

        self.lblMensaje.grid(row=7, column=0, columnspan=2, pady=5)

        self.btnExit.grid(row=8, column=0, columnspan=2, pady=10)

        self.btnExit = Button(root, text="Salir", command=self.salir)
        self.btnExit.grid(row=8, column=0, columnspan=2)

    def extraer_contenido_entre_nombre(self, cadena, nombre_inicio, nombre_fin):
        inicio = cadena.find(nombre_inicio)
        if inicio != -1:
            inicio += len(nombre_inicio)
            fin = cadena.find(nombre_fin, inicio)
            if fin != -1:
                return cadena[inicio:fin]
        return ""

    def consultar_dni_event(self, event):
        self.consultar_dni()

    def consultar_dni(self):
        self.clear_entries()

        numero_dni = self.txtNumeroDNI.get()
        if not numero_dni.strip():
            return

        # Check if DNI has already been registered today
        if self.db.record_exists_today(numero_dni):
            messagebox.showwarning("Consultar DNI", f"El número de DNI {numero_dni} ya fue registrado hoy.")
            self.txtNumeroDNI.delete(0, END)
            return

        self.btnConsultar.config(state=DISABLED)
        start_time = time.time()

        session = self.create_session()
        token = self.get_token(session)

        if token:
            contenido_dni = self.fetch_dni_data(session, token, numero_dni)
            mensaje_respuesta, fecha_hora = self.parse_dni_response(contenido_dni, numero_dni)
        else:
            mensaje_respuesta = f"Ocurrió un inconveniente al consultar el número de DNI {numero_dni}.\nNo se pudo obtener el token."

        elapsed_time = time.time() - start_time
        self.lblMensaje.config(text=f"Procesado en {elapsed_time:.2f} seg.")
        self.btnConsultar.config(state=NORMAL)
        self.txtNumeroDNI.focus()
        self.txtNumeroDNI.select_range(0, END)

        if 'exitosamente' not in mensaje_respuesta:
            messagebox.showwarning("Consultar DNI", mensaje_respuesta)
        else:
            messagebox.showinfo("Consultar DNI", mensaje_respuesta)
            self.agregar_a_tabla(numero_dni, self.txtApellidoPaterno.get(), self.txtApellidoMaterno.get(), self.txtNombres.get(), fecha_hora)
            self.db.insert_record(numero_dni, self.txtApellidoPaterno.get(), self.txtApellidoMaterno.get(), self.txtNombres.get(), fecha_hora)

        # Clear the text entry fields after registering the DNI
        self.txtNumeroDNI.delete(0, END)
        self.txtApellidoPaterno.delete(0, END)
        self.txtApellidoMaterno.delete(0, END)
        self.txtNombres.delete(0, END)

    def clear_entries(self):
        self.txtApellidoPaterno.delete(0, END)
        self.txtApellidoMaterno.delete(0, END)
        self.txtNombres.delete(0, END)

    def create_session(self):
        session = requests.Session()
        session.headers.update({
            "Host": "eldni.com",
            "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"90\", \"Google Chrome\";v=\"90\"",
            "sec-ch-ua-mobile": "?0",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
        })
        return session

    def get_token(self, session):
        url = "https://eldni.com/pe/buscar-por-dni"
        response = session.get(url)
        if response.status_code == 200:
            html = response.text
            return self.extraer_contenido_entre_nombre(html, 'name="_token" value="', '">')
        return None

    def fetch_dni_data(self, session, token, numero_dni):
        session.headers.update({
            "Origin": "https://eldni.com",
            "Referer": "https://eldni.com/pe/buscar-por-dni",
            "Sec-Fetch-Site": "same-origin"
        })

        data = {
            "_token": token,
            "dni": numero_dni
        }

        url = "https://eldni.com/pe/buscar-por-dni"
        response = session.post(url, data=data)
        if response.status_code == 200:
            html = response.text
            tabla_inicio = '<table class="table table-striped table-scroll">'
            tabla_fin = '</table>'
            return self.extraer_contenido_entre_nombre(html, tabla_inicio, tabla_fin)
        return None

    def parse_dni_response(self, contenido_dni, numero_dni):
        if contenido_dni:
            nombre_inicio = '<td>'
            nombre_fin = '</td>'
            arr_resultado = re.findall(f'{nombre_inicio}(.*?){nombre_fin}', contenido_dni)

            if len(arr_resultado) >= 4:
                self.txtApellidoPaterno.insert(0, arr_resultado[2])
                self.txtApellidoMaterno.insert(0, arr_resultado[3])
                self.txtNombres.insert(0, arr_resultado[1])
                mensaje_respuesta = f"Se realizó exitosamente la consulta del número de DNI {numero_dni}"
                fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                mensaje_respuesta = f"No se pudo realizar la consulta del número de DNI {numero_dni}."
                fecha_hora = None
        else:
            mensaje_respuesta = f"No se pudo realizar la consulta del número de DNI {numero_dni}."
            fecha_hora = None

        return mensaje_respuesta, fecha_hora

    def agregar_a_tabla(self, dni, apellido_paterno, apellido_materno, nombres, fecha_hora):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree.insert("", "end", values=(dni, apellido_paterno, apellido_materno, nombres, fecha_hora))

    def guardar_dni(self):
        numero_dni = self.txtNumeroDNI.get()
        apellido_paterno = self.txtApellidoPaterno.get()
        apellido_materno = self.txtApellidoMaterno.get()
        nombres = self.txtNombres.get()
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not (numero_dni and apellido_paterno and apellido_materno and nombres):
            messagebox.showerror("Error", "Todos los campos deben estar llenos")
            return

        if self.db.insert_record(numero_dni, apellido_paterno, apellido_materno, nombres, fecha_hora):
            self.agregar_a_tabla(numero_dni, apellido_paterno, apellido_materno, nombres, fecha_hora)
            messagebox.showinfo("Guardar DNI", "Se registró su asistencia satisfactoriamente")
        else:
            messagebox.showwarning("Guardar DNI", "Ya existe un registro con este DNI en la fecha actual")

        self.txtNumeroDNI.delete(0, END)
        self.txtApellidoPaterno.delete(0, END)
        self.txtApellidoMaterno.delete(0, END)
        self.txtNombres.delete(0, END)

    def restart_application(self):
        self.root.destroy()
        self.restart_callback()

    def salir(self):
        self.root.destroy()
        self.restart_callback()

    def salir(self):
        self.root.destroy()
        self.restart_callback()

    def __del__(self):
        self.db.close()

if __name__ == "__main__":
    def restart_login():
        root = Tk()
        app = FrmConsultaDNI(root, restart_login)
        root.mainloop()

    root = Tk()
    app = FrmConsultaDNI(root, restart_login)
    root.mainloop()


