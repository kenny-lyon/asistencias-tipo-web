from tkinter import *
from _1er_scrip import FrmConsultaDNI
from dni_report import FrmReporteDNI
from datetime import datetime
from PIL import Image, ImageTk

class Login:
    def __init__(self, root):
        self.root = root
        self.root.title("Ingresar")

        # Cargar y mostrar la imagen
        self.img = Image.open("C:/Users/yuliana/OneDrive/Escritorio/DNI registro/Estadistica Informatica.png")
        self.img = self.img.resize((200, 200), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(self.img)
        self.lblImage = Label(root, image=self.photo)
        self.lblImage.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.lblWelcome = Label(root, text="Bienvenido a nuestra prueba de registro de asistencia")
        self.lblWelcome.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Mostrar la fecha y hora actual
        self.lblFecha = Label(root, text="Fecha:")
        self.lblFecha.grid(row=2, column=0, padx=10, pady=10)
        self.lblFechaValue = Label(root, text=datetime.now().strftime("%Y-%m-%d"))
        self.lblFechaValue.grid(row=2, column=1, padx=10, pady=10)

        self.lblHora = Label(root, text="Hora:")
        self.lblHora.grid(row=3, column=0, padx=10, pady=10)
        self.lblHoraValue = Label(root, text=datetime.now().strftime("%H:%M:%S"))
        self.lblHoraValue.grid(row=3, column=1, padx=10, pady=10)

        self.lblPrompt = Label(root, text="¿Cómo desea iniciar?")
        self.lblPrompt.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.btnLoginUser = Button(root, text="Iniciar como Usuario", command=self.login_user)
        self.btnLoginUser.grid(row=5, column=0, padx=10, pady=10)

        self.btnLoginAdmin = Button(root, text="Iniciar como Admin", command=self.show_admin_login)
        self.btnLoginAdmin.grid(row=5, column=1, padx=10, pady=10)

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

        self.lblAdminUser = Label(self.admin_login_window, text="Usuario:")
        self.lblAdminUser.grid(row=0, column=0, padx=10, pady=10)
        self.entryAdminUser = Entry(self.admin_login_window)
        self.entryAdminUser.grid(row=0, column=1, padx=10, pady=10)

        self.lblAdminPassword = Label(self.admin_login_window, text="Contraseña:")
        self.lblAdminPassword.grid(row=1, column=0, padx=10, pady=10)
        self.entryAdminPassword = Entry(self.admin_login_window, show="*")
        self.entryAdminPassword.grid(row=1, column=1, padx=10, pady=10)

        self.btnAdminLogin = Button(self.admin_login_window, text="INGRESAR", command=self.login_admin)
        self.btnAdminLogin.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def login_admin(self):
        username = self.entryAdminUser.get()
        password = self.entryAdminPassword.get()

        if username == "admin" and password == "1234":
            self.admin_login_window.destroy()
            self.root.destroy()
            admin_root = Tk()
            app = FrmReporteDNI(admin_root, self.restart_login)
            admin_root.mainloop()
        else:
            self.lblError = Label(self.admin_login_window, text="Usuario o contraseña incorrectos", fg="red")
            self.lblError.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def restart_login(self):
        root = Tk()
        app = Login(root)
        root.mainloop()

if __name__ == "__main__":
    root = Tk()
    app = Login(root)
    root.mainloop()
