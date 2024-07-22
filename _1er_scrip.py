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
        self.root.title("Registro de Asistencia")
        self.restart_callback = restart_callback

        self.db = DniDatabase()

        self.lblNumeroDNI = Label(root, text="Número DNI:")
        self.lblNumeroDNI.grid(row=0, column=0)
        
        self.txtNumeroDNI = Entry(root)
        self.txtNumeroDNI.grid(row=0, column=1)

        self.btnConsultar = Button(root, text="Consultar DNI", command=self.consultar_dni)
        self.btnConsultar.grid(row=1, column=0, columnspan=2)
        
        self.lblApellidoPaterno = Label(root, text="Apellido Paterno:")
        self.lblApellidoPaterno.grid(row=2, column=0)
        self.txtApellidoPaterno = Entry(root)
        self.txtApellidoPaterno.grid(row=2, column=1)
        
        self.lblApellidoMaterno = Label(root, text="Apellido Materno:")
        self.lblApellidoMaterno.grid(row=3, column=0)
        self.txtApellidoMaterno = Entry(root)
        self.txtApellidoMaterno.grid(row=3, column=1)
        
        self.lblNombres = Label(root, text="Nombres:")
        self.lblNombres.grid(row=4, column=0)
        self.txtNombres = Entry(root)
        self.txtNombres.grid(row=4, column=1)

        self.btnGuardar = Button(root, text="Guardar", command=self.abrir_ventana_guardar)
        self.btnGuardar.grid(row=5, column=0, columnspan=2)

        self.tree = ttk.Treeview(root, columns=("DNI", "Apellido Paterno", "Apellido Materno", "Nombres", "Fecha y Hora de Ingreso", "Fecha y Hora de Salida"), show='headings')
        self.tree.heading("DNI", text="DNI")
        self.tree.heading("Apellido Paterno", text="Apellido Paterno")
        self.tree.heading("Apellido Materno", text="Apellido Materno")
        self.tree.heading("Nombres", text="Nombres")
        self.tree.heading("Fecha y Hora de Ingreso", text="Fecha y Hora de Ingreso")
        self.tree.heading("Fecha y Hora de Salida", text="Fecha y Hora de Salida")
        self.tree.grid(row=6, column=0, columnspan=2)

        self.lblMensaje = Label(root, text="")
        self.lblMensaje.grid(row=7, column=0, columnspan=2)

    def extraer_contenido_entre_nombre(self, cadena, nombre_inicio, nombre_fin):
        inicio = cadena.find(nombre_inicio)
        if inicio != -1:
            inicio += len(nombre_inicio)
            fin = cadena.find(nombre_fin, inicio)
            if fin != -1:
                return cadena[inicio:fin]
        return ""

    def consultar_dni(self):
        self.txtApellidoPaterno.delete(0, END)
        self.txtApellidoMaterno.delete(0, END)
        self.txtNombres.delete(0, END)
        numero_dni = self.txtNumeroDNI.get()

        if not numero_dni.strip():
            return

        self.btnConsultar.config(state=DISABLED)
        start_time = time.time()

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

        url = "https://eldni.com/pe/buscar-por-dni"
        response = session.get(url)
        if response.status_code == 200:
            html = response.text
            token = self.extraer_contenido_entre_nombre(html, 'name="_token" value="', '">')

            session.headers.update({
                "Origin": "https://eldni.com",
                "Referer": "https://eldni.com/pe/buscar-por-dni",
                "Sec-Fetch-Site": "same-origin"
            })

            data = {
                "_token": token,
                "dni": numero_dni
            }
            response = session.post(url, data=data)
            if response.status_code == 200:
                html = response.text
                tabla_inicio = '<table class="table table-striped table-scroll">'
                tabla_fin = '</table>'
                contenido_dni = self.extraer_contenido_entre_nombre(html, tabla_inicio, tabla_fin)

                if contenido_dni:
                    nombre_inicio = '<td>'
                    nombre_fin = '</td>'
                    arr_resultado = re.findall(f'{nombre_inicio}(.*?){nombre_fin}', contenido_dni)

                    if len(arr_resultado) >= 4:
                        self.txtApellidoPaterno.insert(0, arr_resultado[2])
                        self.txtApellidoMaterno.insert(0, arr_resultado[3])
                        self.txtNombres.insert(0, arr_resultado[1])
                        mensaje_respuesta = f"Se realizó la consulta del número de DNI {numero_dni}"
                    else:
                        mensaje_respuesta = f"No se pudo realizar la consulta del número de DNI {numero_dni}."
                else:
                    mensaje_respuesta = f"No se pudo realizar la consulta del número de DNI {numero_dni}."
            else:
                mensaje_respuesta = f"Ocurrió un inconveniente al consultar los datos del DNI {numero_dni}.\nDetalle: {response.text}"
        else:
            mensaje_respuesta = f"Ocurrió un inconveniente al consultar el número de DNI {numero_dni}.\nDetalle: {response.text}"

        elapsed_time = time.time() - start_time
        self.lblMensaje.config(text=f"Procesado en {elapsed_time:.2f} seg.")
        self.btnConsultar.config(state=NORMAL)
        self.txtNumeroDNI.focus()
        self.txtNumeroDNI.select_range(0, END)
        
        if 'exitosamente' not in mensaje_respuesta:
            messagebox.showwarning("Consultar DNI", mensaje_respuesta)
        else:
            messagebox.showinfo("Consultar DNI", mensaje_respuesta)

    def agregar_a_tabla(self, dni, apellido_paterno, apellido_materno, nombres, fecha_hora_ingreso, fecha_hora_salida):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree.insert("", "end", values=(dni, apellido_paterno, apellido_materno, nombres, fecha_hora_ingreso, fecha_hora_salida))

    def abrir_ventana_guardar(self):
        ventana = Toplevel(self.root)
        ventana.title("Registrar Horario")
        
        btnIngreso = Button(ventana, text="Registrar horario de Ingreso", command=lambda: self.registrar_horario("ingreso", ventana))
        btnIngreso.grid(row=0, column=0, padx=20, pady=20)

        btnSalida = Button(ventana, text="Registrar horario de Salida", command=lambda: self.registrar_horario("salida", ventana))
        btnSalida.grid(row=0, column=1, padx=20, pady=20)

    def registrar_horario(self, tipo, ventana):
        numero_dni = self.txtNumeroDNI.get()
        apellido_paterno = self.txtApellidoPaterno.get()
        apellido_materno = self.txtApellidoMaterno.get()
        nombres = self.txtNombres.get()
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not (numero_dni and apellido_paterno and apellido_materno and nombres):
            messagebox.showerror("Error", "Todos los campos deben estar llenos")
            return
        
        # Verificar duplicados para ingreso
        if tipo == "ingreso":
            if self.db.insert_record(numero_dni, apellido_paterno, apellido_materno, nombres, fecha_hora, ""):
                self.agregar_a_tabla(numero_dni, apellido_paterno, apellido_materno, nombres, fecha_hora, "")
                messagebox.showinfo("Guardar DNI", "Se registró su asistencia satisfactoriamente")
            else:
                messagebox.showwarning("Guardar DNI", "Ya existe un registro con este DNI en la fecha actual para ingreso")
        
        # Verificar duplicados para salida
        elif tipo == "salida":
            if self.db.update_record_salida(numero_dni, fecha_hora):
                self.agregar_a_tabla(numero_dni, apellido_paterno, apellido_materno, nombres, "", fecha_hora)
                messagebox.showinfo("Guardar DNI", "Se registró su salida satisfactoriamente")
            else:
                messagebox.showwarning("Guardar DNI", "Ya existe un registro de salida para este DNI en la fecha actual")
        
        # Cerrar la ventana después de guardar
        ventana.destroy()

        # Reiniciar sesión
        self.root.destroy()
        self.restart_callback()

    def __del__(self):
        self.db.close()

if __name__ == "__main__":
    root = Tk()
    app = FrmConsultaDNI(root, None)
    root.mainloop()
