#login:  con esto se inicia los demas codigos ( este es el main )
from tkinter import *
from _1er_scrip import FrmConsultaDNI
from dni_report import FrmReporteDNI

class Login:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")

        self.lblWelcome = Label(root, text="Bienvenido a nuestra prueba de registro de asistencia")
        self.lblWelcome.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.lblPrompt = Label(root, text="¿Cómo desea iniciar?")
        self.lblPrompt.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.btnLoginUser = Button(root, text="Iniciar como Usuario", command=self.login_user)
        self.btnLoginUser.grid(row=2, column=0, padx=10, pady=10)

        self.btnLoginAdmin = Button(root, text="Iniciar como Admin", command=self.login_admin)
        self.btnLoginAdmin.grid(row=2, column=1, padx=10, pady=10)

    def login_user(self):
        self.root.destroy()
        user_root = Tk()
        app = FrmConsultaDNI(user_root, self.restart_login)
        user_root.mainloop()

    def login_admin(self):
        self.root.destroy()
        admin_root = Tk()
        app = FrmReporteDNI(admin_root)
        admin_root.mainloop()

    def restart_login(self):
        root = Tk()
        app = Login(root)
        root.mainloop()

if __name__ == "__main__":
    root = Tk()
    app = Login(root)
    root.mainloop()
