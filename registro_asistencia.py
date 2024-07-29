import wx
import wx.grid as gridlib
from datetime import datetime, timedelta
import calendar
import locale
import subprocess
from dni_database import DniDatabase
from Reporte_semanal import WeeklyReportFrame

# Establecer el locale en español
locale.setlocale(locale.LC_TIME, 'es_ES.utf8')

class RegistroAsistencia(wx.Frame):
    def __init__(self, *args, **kw):
        super(RegistroAsistencia, self).__init__(*args, **kw)

        self.db = DniDatabase()
        self.nombres_registrados = self.obtener_nombres_desde_db()
        self.today = datetime.now()
        self.year = self.today.year
        self.month = self.today.month
        self.InitUI()

    def obtener_nombres_desde_db(self):
        return self.db.fetch_all_names()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Fuente y colores personalizados
        fuente = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        color_fondo = wx.Colour(240, 240, 240)
        color_texto = wx.Colour(0, 0, 0)

        panel.SetBackgroundColour(color_fondo)

        # Botón de cerrar reporte
        close_button = wx.Button(panel, label="Cerrar Reporte")
        close_button.SetFont(fuente)
        close_button.SetBackgroundColour(wx.Colour("#00BFBF"))  # Color cian
        close_button.SetForegroundColour(wx.Colour(255, 255, 255))  # Color blanco
        close_button.Bind(wx.EVT_BUTTON, self.OnCloseReport)
        vbox.Add(close_button, 0, wx.ALL | wx.ALIGN_LEFT, 5)
        
        # Control de mes
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        mes_label = wx.StaticText(panel, label="Aquí puedes cambiar de mes:")
        mes_label.SetFont(fuente)
        hbox.Add(mes_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.month_button = wx.Button(panel, label=self.get_month_name(self.month))
        self.month_button.SetFont(fuente)
        self.month_button.SetBackgroundColour(wx.Colour("#00BFBF"))  # Color cian
        self.month_button.SetForegroundColour(wx.Colour(255, 255, 255))  # Color blanco
        self.month_button.Bind(wx.EVT_BUTTON, self.OnMonthButton)
        hbox.Add(self.month_button, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        # Botón para el reporte semanal
        self.report_button = wx.Button(panel, label="Reporte Semanal")
        self.report_button.SetFont(fuente)
        self.report_button.SetBackgroundColour(wx.Colour("#00BFBF"))  # Color cian
        self.report_button.SetForegroundColour(wx.Colour(255, 255, 255))  # Color blanco
        self.report_button.Bind(wx.EVT_BUTTON, self.OnWeeklyReport)
        hbox.Add(self.report_button, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        vbox.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.grid = gridlib.Grid(panel)
        vbox.Add(self.grid, 1, wx.EXPAND)

        panel.SetSizer(vbox)
        
        # Ocultar etiquetas de filas y columnas
        self.grid.HideRowLabels()
        self.grid.HideColLabels()
        
        # Crear la cuadrícula inicialmente con un tamaño mínimo
        self.grid.CreateGrid(1, 1)

        self.UpdateGrid()

        self.SetTitle('Reporte Mensual')
        self.Centre()
        self.SetSize(1100,600) # Ajusta el tamaño de la ventana según tus necesidades

    def get_month_name(self, month):
        return datetime(self.year, month, 1).strftime("%B").capitalize()

    def OnMonthButton(self, event):
        months = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        dlg = wx.SingleChoiceDialog(self, "Selecciona un mes", "Mes", months)

        if dlg.ShowModal() == wx.ID_OK:
            month_name = dlg.GetStringSelection()
            self.month = months.index(month_name) + 1
            self.month_button.SetLabel(month_name)
            self.UpdateGrid()
            
    def OnCloseReport(self, event):
        self.Close()  # Cierra la ventana wxPython
        # Reinicia la aplicación Tkinter
        subprocess.Popen(["python", "dni_report.py"])  # Reemplaza 'reporte_dni.py' con el nombre del archivo correcto
        
    def UpdateGrid(self):
        self.grid.ClearGrid()

        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(self.year, self.month)
        num_dias_mes = (datetime(self.year, self.month % 12 + 1, 1) - timedelta(days=1)).day
        num_weeks = len(month_days)
        total_cols = num_weeks * 7 + 4  # Total de días del mes + columnas adicionales
        num_rows = len(self.nombres_registrados) + 4  # 4 filas para encabezados

        # Redimensionar la cuadrícula
        self.grid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.grid.SetDefaultCellBackgroundColour(wx.Colour(255, 255, 255))

        # Ajustar el tamaño de la cuadrícula
        if self.grid.GetNumberRows() < num_rows:
            self.grid.AppendRows(num_rows - self.grid.GetNumberRows())
        elif self.grid.GetNumberRows() > num_rows:
            self.grid.DeleteRows(num_rows, self.grid.GetNumberRows() - num_rows)

        if self.grid.GetNumberCols() < total_cols:
            self.grid.AppendCols(total_cols - self.grid.GetNumberCols())
        elif self.grid.GetNumberCols() > total_cols:
            self.grid.DeleteCols(total_cols, self.grid.GetNumberCols() - total_cols)

        dias_semana = ['L', 'M', 'X', 'J', 'V', 'S', 'D']

        # Fila de nombre del mes
        self.grid.SetCellValue(0, 1, self.get_month_name(self.month))
        self.grid.SetCellSize(0, 1, 1, num_weeks * 7)
        self.grid.SetCellAlignment(0, 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Encabezado "NOMBRES"
        self.grid.SetCellValue(1, 0, "NOMBRES")
        self.grid.SetCellSize(1, 0, 3, 1)
        self.grid.SetCellAlignment(1, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Ajustar los encabezados de semanas y días del mes
        col = 1
        for week_index, week in enumerate(month_days):
            self.grid.SetCellValue(1, col, f"SEMANA {week_index + 1:02}")
            self.grid.SetCellSize(1, col, 1, 7)
            self.grid.SetCellAlignment(1, col, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            
            for day_index, day in enumerate(week):
                if day != 0:
                    self.grid.SetCellValue(2, col, dias_semana[day_index])
                    self.grid.SetCellAlignment(2, col, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                    self.grid.SetCellValue(3, col, str(day))
                    self.grid.SetCellAlignment(3, col, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                col += 1

        # Encabezados "ASISTENCIA", "% DE ASISTENCIA" y "FALTAS"
        asistencia_headers = ["ASISTENCIA", "% DE\n ASISTENCIA", "FALTAS"]
        for i, header in enumerate(asistencia_headers):
            col_index = total_cols - len(asistencia_headers) + i
            self.grid.SetCellValue(1, col_index, header)
            self.grid.SetCellSize(1, col_index, 3, 1)
            self.grid.SetCellAlignment(1, col_index, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Obtener registros de asistencia para el mes
        registros = self.db.fetch_records_by_month(self.year, self.month)

        # Insertar datos de asistencia
        for row, nombre in enumerate(self.nombres_registrados, start=4):
            self.grid.SetCellValue(row, 0, nombre)
            estado_asistencia = [''] * num_dias_mes

            for registro in registros:
                if registro[1] == nombre:
                    dia = int(registro[2].split('-')[2].split()[0])
                    if registro[3]:  # Hay fecha de salida
                        estado_asistencia[dia-1] = '✓'
                    elif registro[2]:  # Solo fecha de ingreso
                        estado_asistencia[dia-1] = '✓'

            for col, estado in enumerate(estado_asistencia, start=1):
                dia_actual = col
                fecha_actual = datetime(self.year, self.month, dia_actual)
                if estado == '✓':
                    self.grid.SetCellValue(row, col, estado)
                    self.grid.SetCellBackgroundColour(row, col, wx.Colour(173, 255, 47))
                elif fecha_actual < self.today:
                    self.grid.SetCellValue(row, col, 'X')
                    self.grid.SetCellBackgroundColour(row, col, wx.Colour(255, 69, 0))
                else:
                    self.grid.SetCellBackgroundColour(row, col, wx.Colour(255, 255, 255))

            asistencia = estado_asistencia.count('✓')
            self.grid.SetCellValue(row, total_cols - 3, str(asistencia))
            porcentaje_asistencia = (asistencia / num_dias_mes) * 100
            self.grid.SetCellValue(row, total_cols - 2, f"{porcentaje_asistencia:.2f}%")
            faltas = num_dias_mes - asistencia
            self.grid.SetCellValue(row, total_cols - 1, str(faltas))

        # Ajustar tamaño de las celdas
        self.grid.AutoSize()
        self.grid.ForceRefresh()
        
    def OnPrevWeek(self, event):
        self.current_week_start -= timedelta(days=7)
        self.current_week_end = self.current_week_start + timedelta(days=6)
        self.UpdateWeeklyGrid()

    def OnNextWeek(self, event):
        self.current_week_start += timedelta(days=7)
        self.current_week_end = self.current_week_start + timedelta(days=6)
        self.UpdateWeeklyGrid()
    

    def OnWeeklyReport(self, event):
        week_number = self.get_current_week_number()
        dialog = wx.MessageDialog(self, f"Semana actual: {week_number}", "Reporte Semanal", wx.OK)
        dialog.ShowModal()
        dialog.Destroy()

        week_start, week_end = self.get_week_start_end_dates(week_number)
        
        self.week_start = week_start
        self.week_end = week_end
        
        reporte_semanal = WeeklyReportFrame(self)
        reporte_semanal.Show()

    def get_current_week_number(self):
        return (self.today - datetime(self.year, 1, 1)).days // 7 + 1

    def get_week_start_end_dates(self, week_number):
        year_start = datetime(self.year, 1, 1)
        week_start = year_start + timedelta(days=(week_number - 1) * 7)
        week_end = week_start + timedelta(days=6)
        return week_start, week_end


if __name__ == '__main__':
    app = wx.App()
    frame = RegistroAsistencia(None)
    frame.Show()
    app.MainLoop()

