import requests
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
import time
import re
from dni_database import DniDatabase

class AttendanceManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Manager")
        self.db = DniDatabase()

        self.create_widgets()

    def create_widgets(self):
        self.root.configure(bg='#CCCCCC')

        # Styles
        style = ttk.Style()
        style.configure('TButton', background='#28A745', foreground='white', font=('Arial', 10, 'bold'))
        style.configure('TLabel', background='#FFC107', font=('Arial', 12, 'bold'))
        style.configure('Treeview', background='#E6E6E6', foreground='#000000', font=('Arial', 10))
        style.configure('Treeview.Heading', background='#28A745', foreground='white', font=('Arial', 11, 'bold'))

        # DNI input
        ttk.Label(self.root, text="DNI:").grid(row=0, column=0, padx=10, pady=10, sticky=W)
        self.dni_entry = ttk.Entry(self.root, font=('Arial', 10))
        self.dni_entry.grid(row=0, column=1, padx=10, pady=10, sticky=W)

        self.search_button = ttk.Button(self.root, text="Search DNI", command=self.search_dni)
        self.search_button.grid(row=0, column=2, padx=10, pady=10)

        # User details
        ttk.Label(self.root, text="First Name:").grid(row=1, column=0, padx=10, pady=10, sticky=W)
        self.first_name_entry = ttk.Entry(self.root, font=('Arial', 10))
        self.first_name_entry.grid(row=1, column=1, padx=10, pady=10, sticky=W)

        ttk.Label(self.root, text="Last Name:").grid(row=2, column=0, padx=10, pady=10, sticky=W)
        self.last_name_entry = ttk.Entry(self.root, font=('Arial', 10))
        self.last_name_entry.grid(row=2, column=1, padx=10, pady=10, sticky=W)

        ttk.Label(self.root, text="Middle Name:").grid(row=3, column=0, padx=10, pady=10, sticky=W)
        self.middle_name_entry = ttk.Entry(self.root, font=('Arial', 10))
        self.middle_name_entry.grid(row=3, column=1, padx=10, pady=10, sticky=W)

        # Register buttons
        self.register_entry_button = ttk.Button(self.root, text="Register Entry", command=lambda: self.register_attendance("entry"))
        self.register_entry_button.grid(row=4, column=0, padx=10, pady=10)

        self.register_exit_button = ttk.Button(self.root, text="Register Exit", command=lambda: self.register_attendance("exit"))
        self.register_exit_button.grid(row=4, column=1, padx=10, pady=10)

        # Attendance table
        columns = ("DNI", "First Name", "Last Name", "Middle Name", "Entry Time", "Exit Time")
        self.attendance_table = ttk.Treeview(self.root, columns=columns, show='headings')
        for col in columns:
            self.attendance_table.heading(col, text=col)
        self.attendance_table.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    def search_dni(self):
        dni = self.dni_entry.get().strip()
        if not dni:
            return

        self.search_button.config(state=DISABLED)
        start_time = time.time()

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0"
        })

        url = "https://eldni.com/pe/buscar-por-dni"
        response = session.get(url)
        if response.status_code == 200:
            html = response.text
            token = self.extract_token(html)

            if token:
                session.headers.update({
                    "Origin": "https://eldni.com",
                    "Referer": url
                })

                data = {
                    "_token": token,
                    "dni": dni
                }

                response = session.post(url, data=data)
                if response.status_code == 200:
                    html = response.text
                    user_data = self.extract_user_data(html)
                    if user_data:
                        self.fill_user_fields(user_data)
                        message = f"DNI {dni} found successfully."
                    else:
                        message = f"DNI {dni} not found."
                else:
                    message = f"Error searching for DNI {dni}: {response.text}"
            else:
                message = f"Unable to extract token for DNI {dni} search."
        else:
            message = f"Error accessing DNI search page: {response.text}"

        elapsed_time = time.time() - start_time
        self.search_button.config(state=NORMAL)
        messagebox.showinfo("Search Result", f"{message}\nProcessed in {elapsed_time:.2f} seconds.")

    def extract_token(self, html):
        return self.extract_between(html, 'name="_token" value="', '">')

    def extract_user_data(self, html):
        table_start = '<table class="table table-striped table-scroll">'
        table_end = '</table>'
        table_content = self.extract_between(html, table_start, table_end)
        if table_content:
            return re.findall('<td>(.*?)</td>', table_content)
        return []

    def extract_between(self, text, start, end):
        try:
            return text.split(start)[1].split(end)[0]
        except IndexError:
            return ""

    def fill_user_fields(self, data):
        if len(data) >= 4:
            self.first_name_entry.delete(0, END)
            self.first_name_entry.insert(0, data[1])
            self.last_name_entry.delete(0, END)
            self.last_name_entry.insert(0, data[2])
            self.middle_name_entry.delete(0, END)
            self.middle_name_entry.insert(0, data[3])

    def register_attendance(self, type_):
        dni = self.dni_entry.get().strip()
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        middle_name = self.middle_name_entry.get().strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not (dni and first_name and last_name and middle_name):
            messagebox.showerror("Error", "All fields must be filled.")
            return

        if type_ == "entry":
            if self.db.insert_record(dni, first_name, last_name, middle_name, timestamp, ""):
                self.update_table(dni, first_name, last_name, middle_name, timestamp, "")
                messagebox.showinfo("Success", "Entry registered successfully.")
            else:
                messagebox.showwarning("Warning", "Entry already registered for this DNI today.")
        else:
            if self.db.update_record_exit(dni, timestamp):
                self.update_table(dni, first_name, last_name, middle_name, "", timestamp)
                messagebox.showinfo("Success", "Exit registered successfully.")
            else:
                messagebox.showwarning("Warning", "Exit already registered for this DNI today.")

        self.clear_fields()

    def update_table(self, dni, first_name, last_name, middle_name, entry_time, exit_time):
        self.attendance_table.insert("", "end", values=(dni, first_name, last_name, middle_name, entry_time, exit_time))

    def clear_fields(self):
        self.dni_entry.delete(0, END)
        self.first_name_entry.delete(0, END)
        self.last_name_entry.delete(0, END)
        self.middle_name_entry.delete(0, END)
        self.dni_entry.focus()

if __name__ == "__main__":
    root = Tk()
    app = AttendanceManager(root)
    root.mainloop()
