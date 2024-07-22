from tkinter import *
from _1er_scrip import FrmConsultaDNI
from dni_report import FrmReporteDNI
from datetime import datetime
from PIL import Image, ImageTk

class Login:
    def __init__(self, root):
        self.root = root
        self.root.title("Registro de Asistencia")
        self.root.geometry("480x500")
        self.root.configure(bg="#2C3E50")  # Fondo azul oscuro

        # Cargar y mostrar la imagen
        self.img = Image.open("C:/Users/KENNY/Downloads/Estadistica Informatica.png")
        self.img = self.img.resize((200, 200), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(self.img)
        self.lblImage = Label(root, image=self.photo, bg="#2C3E50")
        self.lblImage.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Etiqueta de bienvenida
        self.lblWelcome = Label(root, text="Registro de Asistencia", font=("Helvetica", 16, "bold"), bg="#2C3E50", fg="#ECF0F1")
        self.lblWelcome.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Mostrar la fecha y hora actual
        self.lblFecha = Label(root, text="Fecha:", font=("Helvetica", 12), bg="#2C3E50", fg="#ECF0F1")
        self.lblFecha.grid(row=2, column=0, padx=10, pady=10, sticky=E)
        self.lblFechaValue = Label(root, text=datetime.now().strftime("%Y-%m-%d"), font=("Helvetica", 12), bg="#2C3E50", fg="#ECF0F1")
        self.lblFechaValue.grid(row=2, column=1, padx=10, pady=10, sticky=W)

        self.lblHora = Label(root, text="Hora:", font=("Helvetica", 12), bg="#2C3E50", fg="#ECF0F1")
        self.lblHora.grid(row=3, column=0, padx=10, pady=10, sticky=E)
        self.lblHoraValue = Label(root, text=datetime.now().strftime("%H:%M:%S"), font=("Helvetica", 12), bg="#2C3E50", fg="#ECF0F1")
        self.lblHoraValue.grid(row=3, column=1, padx=10, pady=10, sticky=W)

        # Etiqueta de solicitud
        self.lblPrompt = Label(root, text="¿Cómo desea iniciar?", font=("Helvetica", 14, "bold"), bg="#2C3E50", fg="#ECF0F1")
        self.lblPrompt.grid(row=4, column=0, columnspan=2, padx=10, pady=20)

        # Botón de inicio de sesión como usuario
        self.btnLoginUser = Button(root, text="Iniciar como Usuario", command=self.login_user, width=20, bg="#27AE60", fg="white", font=("Helvetica", 12, "bold"), relief=RAISED, bd=2)
        self.btnLoginUser.grid(row=5, column=0, padx=10, pady=10, ipadx=5, ipady=5)

        # Botón de inicio de sesión como administrador
        self.btnLoginAdmin = Button(root, text="Iniciar como Admin", command=self.show_admin_login, width=20, bg="#2980B9", fg="white", font=("Helvetica", 12, "bold"), relief=RAISED, bd=2)
        self.btnLoginAdmin.grid(row=5, column=1, padx=10, pady=10, ipadx=5, ipady=5)

        # Actualizar la hora cada segundo
        self.update_time()

    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.lblHoraValue.config(text=current_time)
        self.root.after(1000, self.update_time)  # Volver a llamar a esta función después de 1 segundo

    def login_user(self):
        self.root.destroy()
        user_root = Tk()
        app = FrmConsultaDNI(user_root, self.restart_login)
        user_root.mainloop()

    def show_admin_login(self):
        self.admin_login_window = Toplevel(self.root)
        self.admin_login_window.title("Admin Login")
        self.admin_login_window.geometry("350x200")
        self.admin_login_window.configure(bg="#34495E")  # Fondo gris oscuro

        self.lblAdminUser = Label(self.admin_login_window, text="Usuario:", font=("Helvetica", 12), bg="#34495E", fg="#ECF0F1")
        self.lblAdminUser.grid(row=0, column=0, padx=10, pady=10, sticky=E)
        self.entryAdminUser = Entry(self.admin_login_window, font=("Helvetica", 12))
        self.entryAdminUser.grid(row=0, column=1, padx=10, pady=10)

        self.lblAdminPassword = Label(self.admin_login_window, text="Contraseña:", font=("Helvetica", 12), bg="#34495E", fg="#ECF0F1")
        self.lblAdminPassword.grid(row=1, column=0, padx=10, pady=10, sticky=E)
        self.entryAdminPassword = Entry(self.admin_login_window, show="*", font=("Helvetica", 12))
        self.entryAdminPassword.grid(row=1, column=1, padx=10, pady=10)

        self.btnAdminLogin = Button(self.admin_login_window, text="INGRESAR", command=self.login_admin, width=20, bg="#008000", fg="white", font=("Helvetica", 12, "bold"), relief=RAISED, bd=2)
        self.btnAdminLogin.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.lblError = Label(self.admin_login_window, text="", fg="red", font=("Helvetica", 12), bg="#34495E")
        self.lblError.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def login_admin(self):
        username = self.entryAdminUser.get()
        password = self.entryAdminPassword.get()

        if username == "76645011" and password == "12345":
            self.admin_login_window.destroy()
            self.root.destroy()
            admin_root = Tk()
            app = FrmReporteDNI(admin_root, self.restart_login)
            admin_root.mainloop()
        else:
            self.lblError.config(text="Usuario o contraseña incorrectos")

    def restart_login(self):
        root = Tk()
        app = Login(root)
        root.mainloop()

if __name__ == "__main__":
    root = Tk()
    app = Login(root)
    root.mainloop()
