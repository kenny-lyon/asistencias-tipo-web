import wx
import wx.grid as gridlib
from datetime import datetime, timedelta

class WeeklyReportFrame(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="Reporte Semanal", size=(650, 400))
        
        self.parent = parent
        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # Botones para cambiar la semana
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.prev_week_button = wx.Button(self.panel, label="< Semana Anterior")
        self.next_week_button = wx.Button(self.panel, label="Semana Siguiente >")
        self.prev_week_button.Bind(wx.EVT_BUTTON, self.OnPrevWeek)
        self.next_week_button.Bind(wx.EVT_BUTTON, self.OnNextWeek)
        
        hbox.Add(self.prev_week_button, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox.Add(self.next_week_button, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.vbox.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.grid = gridlib.Grid(self.panel)
        self.vbox.Add(self.grid, 1, wx.EXPAND)
        self.panel.SetSizer(self.vbox)

        self.current_week_start = self.parent.today - timedelta(days=self.parent.today.weekday())
        self.current_week_end = self.current_week_start + timedelta(days=6)

        self.InitUI()

    def InitUI(self):
        self.grid.CreateGrid(1, 1)
        self.UpdateWeeklyGrid()
        self.Centre()

    def UpdateWeeklyGrid(self):
        self.grid.ClearGrid()

        total_cols = 8 + 2  # 7 días de la semana + columnas adicionales
        num_rows = len(self.parent.nombres_registrados) + 3  # 3 filas para encabezados

        # Redimensionar la cuadrícula
        self.grid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.grid.SetDefaultCellBackgroundColour(wx.Colour(240, 240, 240))

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

        # Fila de nombre de la semana
        self.grid.SetCellValue(0, 1, f"Semana del {self.current_week_start.strftime('%d/%m/%Y')} al {self.current_week_end.strftime('%d/%m/%Y')}")
        self.grid.SetCellSize(0, 1, 1, 7)
        self.grid.SetCellAlignment(0, 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Encabezado "NOMBRES"
        self.grid.SetCellValue(1, 0, "NOMBRES")
        self.grid.SetCellSize(1, 0, 2, 1)
        self.grid.SetCellAlignment(1, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Ajustar los encabezados de días de la semana
        col = 1
        for day_index in range(7):
            self.grid.SetCellValue(1, col, dias_semana[day_index])
            self.grid.SetCellAlignment(1, col, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            col += 1

        # Encabezados "ASISTENCIA" y "FALTAS"
        asistencia_headers = ["ASISTENCIA", "FALTAS"]
        for i, header in enumerate(asistencia_headers):
            col_index = total_cols - len(asistencia_headers) + i
            self.grid.SetCellValue(1, col_index, header)
            self.grid.SetCellSize(1, col_index, 2, 1)
            self.grid.SetCellAlignment(1, col_index, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Obtener registros de asistencia para la semana seleccionada
        registros = self.parent.db.fetch_records_by_date_range(self.current_week_start, self.current_week_end)

        # Insertar datos de asistencia
        for row, nombre in enumerate(self.parent.nombres_registrados, start=3):
            self.grid.SetCellValue(row, 0, nombre)
            estado_asistencia = [''] * 7

            for registro in registros:
                if registro[1] == nombre:
                    fecha_registro = datetime.strptime(registro[2], "%Y-%m-%d %H:%M:%S")
                    dia_semana = fecha_registro.weekday()
                    if registro[3]:  # Hay fecha de salida
                        estado_asistencia[dia_semana] = '✓'
                    elif registro[2]:  # Solo fecha de ingreso
                        estado_asistencia[dia_semana] = '✓'

            for col, estado in enumerate(estado_asistencia, start=1):
                fecha_actual = self.current_week_start + timedelta(days=col-1)
                if estado == '✓':
                    self.grid.SetCellValue(row, col, estado)
                    self.grid.SetCellBackgroundColour(row, col, wx.Colour(0, 255, 0))
                elif fecha_actual < self.parent.today and not estado:  # Falta (sin registro)
                    self.grid.SetCellValue(row, col, 'X')
                    self.grid.SetCellBackgroundColour(row, col, wx.Colour(255, 0, 0))
                elif fecha_actual >= self.parent.today:  # Fechas futuras no se pintan
                    self.grid.SetCellValue(row, col, '')
                    self.grid.SetCellBackgroundColour(row, col, wx.Colour(255, 255, 255))

            # Datos calculados de asistencia y faltas
            asistencia = sum(1 for estado in estado_asistencia if estado == '✓')
            faltas = sum(1 for estado in estado_asistencia if estado == 'X')

            self.grid.SetCellValue(row, total_cols - 2, str(asistencia))
            self.grid.SetCellBackgroundColour(row, total_cols - 2, wx.Colour(255, 255, 255))  # Color blanco para celda de "ASISTENCIA"
            self.grid.SetCellValue(row, total_cols - 1, str(faltas))
            self.grid.SetCellBackgroundColour(row, total_cols - 1, wx.Colour(255, 255, 255))  # Color blanco para celda de "FALTAS"

        # Ajustar el tamaño de las columnas para que sean proporcionales
        self.grid.SetColSize(0, 150)  # Ajustar la columna de nombres
        for i in range(1, total_cols - 2):
            self.grid.SetColSize(i, 40)

        self.grid.HideRowLabels()
        self.grid.HideColLabels()

    def OnPrevWeek(self, event):
        self.current_week_start -= timedelta(days=7)
        self.current_week_end = self.current_week_start + timedelta(days=6)
        self.UpdateWeeklyGrid()

    def OnNextWeek(self, event):
        self.current_week_start += timedelta(days=7)
        self.current_week_end = self.current_week_start + timedelta(days=6)
        self.UpdateWeeklyGrid()
