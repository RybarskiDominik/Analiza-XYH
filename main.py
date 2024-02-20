from PySide6.QtWidgets import (QApplication, QDockWidget, QMainWindow,
                                QTableWidget, QFileDialog, QTableWidgetItem, QWidget)
from PySide6.QtCore import Qt
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtGui import QIcon
from lista import NewDragDropWidget

import pandas as pd
import numpy as np
import webbrowser
import sys
import re
import os


if getattr(sys, 'frozen', False): #and hasattr(sys, '_MEIPASS'):
    path_obrazy = os.path.dirname(sys.executable) + '\\Obrazy\\'
else:
    path_obrazy = sys.path[0] + '\\Obrazy\\'


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow,self).__init__()
        self.setWindowTitle("Porównanie współrzednych")
        self.setWindowIcon(QIcon(path_obrazy + 'WSP.ico'))
        self.setBaseSize(700,430)
        self.setMinimumSize(700,430)
        self.setMaximumSize(1100,430)
        self.setAcceptDrops(True)
        self.new_drag_drop_widget = None
        
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        pd.options.display.float_format = '{:.2f}'.format

        self.df_1 = pd.DataFrame()
        self.df_2 = pd.DataFrame()
        self.df_3 = pd.DataFrame()
        self.df_memory = pd.DataFrame()
        self.df_list_1 = pd.DataFrame()
        self.df_list_2 = pd.DataFrame()

        self.bimport = QtWidgets.QPushButton(self)
        self.bimport.setText("Import TXT")
        self.bimport.setGeometry(0, 2, 70, 28)
        self.bimport.clicked.connect(self.import_TXT)
        self.bimport.setToolTip('<p style="margin: 0;">Wczytaj <b>"TXT"</b> do pamięci.</p>'
                                    '<p style="margin: 0;">Format:</p>'
                                    '<p style="margin: 0;"><b>-NR X Y H</b> (<b>*H</b> nie jest wymagane)</p>'
                                    '<p style="margin: 2;"><b>Zduplikowane numery</b> są usuwane automatycznie!!!</p>'
                                    '<p style="margin: 10;"><b>Możesz także przerzucić plik *txt do konkretnej tabeli.</b></p>')

        self.status = QtWidgets.QLineEdit(self)
        #self.status.setText("Txt")
        self.status.setReadOnly(True)
        self.status.setGeometry(70, 3, 26, 26)
        self.status.setStyleSheet("background-color: #686868")
        self.status.setToolTip('<p style="margin: 0;">Status <b>"TXT"</b></p>'
                                '<p style="margin: 0;"><b>Kolory oznaczają:</b></p>'
                                '<p style="margin: 0;">-<b style="color: gray;">szary</b> pusta pamięć.</p>'
                                '<p style="margin: 0;">-<b style="color: green;">zielony</b> poprawne wczytanie pliku <b>TXT</b>.</p>'
                                '<p style="margin: 0;">-<b style="color: red;">czerwony</b> pamięć została wyczyszczona.</p>')

        self.b2 = QtWidgets.QPushButton(self)
        self.b2.setText("Export")
        self.b2.setGeometry(96, 2, 70, 28)
        self.b2.clicked.connect(self.export_TXT)
        self.b2.setToolTip('<p>Export do programu <b>EXCEL</b>.</p>')

        #self.alltable = QtWidgets.QToolButton(self)
        self.alltable = QtWidgets.QPushButton(self)
        #self.alltable.setText("Exchange")
        self.alltable.setIcon(QtGui.QIcon(path_obrazy + 'Exchange.svg'))
        self.alltable.setIconSize(QtCore.QSize(30, 28))
        self.alltable.setGeometry(180, 2, 40, 28)
        self.alltable.clicked.connect(lambda: self.run_sort("L", True, name = "NR", Name_left_column = "Lista punktów tabela nr 1:", Name_right_column = "Lista punktów tabela nr 2:"))
        self.alltable.setToolTip('<p>Ręczne porządkowanie tabel.</p>')

        self.lefttable = QtWidgets.QToolButton(self)
        #self.lefttable = QtWidgets.QPushButton(self)
        #self.lefttable.setText("Left")
        self.lefttable.setIcon(QtGui.QIcon(path_obrazy + 'Left.svg'))
        self.lefttable.setIconSize(QtCore.QSize(26, 26))
        self.lefttable.setGeometry(222, 2, 28, 28)
        self.lefttable.clicked.connect(lambda: self.run_sort("L", False, name = "NR"))
        self.lefttable.setToolTip('<p>Wprowadź ręcznie dane dla lewej tabeli.</p>')

        self.righttable = QtWidgets.QToolButton(self)
        #self.righttable.setText("Right")
        self.righttable.setIcon(QtGui.QIcon(path_obrazy + 'Right.svg'))
        self.righttable.setIconSize(QtCore.QSize(26, 26))
        self.righttable.setGeometry(250, 2, 28, 28)
        self.righttable.clicked.connect(lambda: self.run_sort("R", False, name = "NR"))
        self.righttable.setToolTip('<p>Wprowadź ręcznie dane dla prawej tabeli.</p>')

        self.b3 = QtWidgets.QPushButton(self)
        self.b3.setText("Rozdziel")
        self.b3.setGeometry(294, 2, 50, 28)
        self.b3.clicked.connect(self.separation)
        self.b3.setToolTip('<p>Program stara się sam rozdzielić dane z lewej tabeli.</p>'
                            '<p style="margin: 0;">W <b>lewej</b> tabeli pozostają numery bez liter.</p>'
                            '<p style="margin: 0;">W <b>prawej</b> tabeli pozostają numery z literami.</p>')
        

        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("Przyporządkuj")
        self.b1.setGeometry(344, 2, 80, 28)
        self.b1.clicked.connect(lambda: self.assign(self.df_1, self.df_2))
        self.b1.setToolTip('<p>Program stara się sam przyporządkować dane z lewej oraz prawej tabeli.</p>')

        self.Donat = QtWidgets.QPushButton(self)
        self.Donat.setText("Donate")
        self.Donat.setGeometry(440, 3, 60, 26)
        self.Donat.setIcon(QtGui.QIcon(path_obrazy + "PayPal.svg"))
        self.Donat.clicked.connect(self.open_edge)

        self.reset = QtWidgets.QToolButton(self)
        self.reset.setIcon(QtGui.QIcon(path_obrazy + 'kosz.svg'))
        self.reset.setIconSize(QtCore.QSize(30, 30))
        self.reset.setGeometry(517, 2, 36, 28)
        self.reset.clicked.connect(self.reset_table)
        self.reset.setToolTip("Czyszczona jest cała pamięć programu.")

        self.b5 = QtWidgets.QPushButton(self)
        self.b5.setText("Twórz")
        self.b5.setGeometry(570, 2, 70, 28)
        self.b5.clicked.connect(lambda: self.createnew(self.df_1, self.df_2))
        self.b5.setToolTip("Tworzy punkty w prawej tabeli.")

        self.b4 = QtWidgets.QPushButton(self)
        self.b4.setText("Oblicz")
        self.b4.setGeometry(640, 2, 60, 28)
        self.b4.clicked.connect(self.oblicz)

        self.table1 = QTableWidget(self)
        self.table1.setColumnCount(4) 
        self.table1.setGeometry(0, 30, 250, 400)
        self.table1.setObjectName("NR1")
        self.table1.resizeColumnsToContents()
        column_headers = ['NR', 'X', 'Y', 'H']
        self.table1.setHorizontalHeaderLabels(column_headers)

        self.table2 = QTableWidget(self)
        self.table2.setColumnCount(4) 
        self.table2.setGeometry(250, 30, 250, 400)
        self.table2.setObjectName("NR2")
        self.table2.resizeColumnsToContents()
        column_headers = ['NR', 'X', 'Y', 'H']
        self.table2.setHorizontalHeaderLabels(column_headers)

        self.table3 = QTableWidget(self)
        self.table3.setGeometry(500, 30, 200, 400)
        self.table3.setColumnCount(4) 
        self.table3.setAcceptDrops(False)
        self.table3.resizeColumnsToContents() 
        self.table2.setObjectName("Wynik")
        column_headers = ['DX', 'DY', 'DH', 'DL']
        self.table3.setHorizontalHeaderLabels(column_headers)

        self.table1.verticalScrollBar().valueChanged.connect(self.syncTables)
        self.table1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table1.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table1.verticalHeader().setVisible(False)

        self.table2.verticalScrollBar().valueChanged.connect(self.syncTables)
        self.table2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)   
        self.table2.verticalHeader().setVisible(False)

        self.table3.verticalScrollBar().valueChanged.connect(self.syncTables)
        self.table3.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table3.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table3.verticalHeader().setVisible(False)

    def synchronize(self, Table):
        print("synchronize")
        if Table == "L":
            matching_rows = self.df_memory[self.df_memory['NR'].isin(self.df_list_1['Sorted'])]
            self.df_1 = matching_rows.reset_index(drop=True)
            self.setup_table(self.table1, self.df_1)
        elif Table == "R":
            matching_rows = self.df_memory[self.df_memory['NR'].isin(self.df_list_2['Sorted'])]
            self.df_2 = matching_rows.reset_index(drop=True)
            self.setup_table(self.table2, self.df_2)

    def synchronize_manual(self):
        print("synchronize manual")

        merge_df = pd.concat([self.df_1, self.df_2], ignore_index=True)
        df_synchro = merge_df.drop_duplicates(subset="NR")
        
        try:
            matching_rows1 = df_synchro[df_synchro['NR'].isin(self.df_list_1['Sorted'])]
            self.df_1 = matching_rows1.reset_index(drop=True)
            self.df_list_1 = self.df_list_1.rename(columns = {'Sorted': 'NR'})
            self.df_1 = self.df_1.set_index('NR')
            self.df_1 = self.df_1.reindex(index=self.df_list_1['NR'])
            self.df_1 = self.df_1.reset_index()
            self.setup_table(self.table1, self.df_1)
        except Exception as e:
                print(e)

        try:
            matching_rows2 = df_synchro[df_synchro['NR'].isin(self.df_list_2['Sorted'])]
            self.df_2 = matching_rows2.reset_index(drop=True)
            self.df_list_2 = self.df_list_2.rename(columns = {'Sorted': 'NR'})
            self.df_2 = self.df_2.set_index('NR')
            self.df_2 = self.df_2.reindex(index=self.df_list_2['NR'])
            self.df_2 = self.df_2.reset_index()
            self.setup_table(self.table2, self.df_2)
        except Exception as e:
            print(e)

    def createnew(self, df1, df2):
        try:
            df1 = df1.copy()
            df1['NR'] = df1['NR'] + "k"
            df1['X'] += np.random.uniform(-0.07, 0.07, size=len(df1))
            df1['Y'] += np.random.uniform(-0.07, 0.07, size=len(df1))
            try:
                df1['H'] += np.random.uniform(-0.03, 0.07, size=len(df1))
            except Exception as e:
                print(e)
                pass
        except Exception as e:
            print(e)

        self.df_2 = df1

        self.setup_table(self.table2, self.df_2)

    def syncTables(self, value):
        sender = self.sender()
        self.table1.horizontalScrollBar().blockSignals(True)
        self.table2.horizontalScrollBar().blockSignals(True)
        self.table3.horizontalScrollBar().blockSignals(True)

        self.table1.verticalScrollBar().setValue(value)
        self.table2.verticalScrollBar().setValue(value)
        self.table3.verticalScrollBar().setValue(value)

        self.table1.horizontalScrollBar().blockSignals(False)
        self.table2.horizontalScrollBar().blockSignals(False)
        self.table3.horizontalScrollBar().blockSignals(False)

    def assign(self, df1, df2):
        if self.df_1.empty or self.df_2.empty:
            print("Empty")
            return
        df_def = pd.DataFrame()

        df1['Numer'] = df1['NR'].astype(str).str.extract(r'(\d+)')
        df2['Numer'] = df2['NR'].astype(str).str.extract(r'(\d+)')
        
        df_def['Numer'] = df2['Numer']

        df2 = pd.merge(df2, df1[['Numer']], how='outer', on=['Numer'])
        df1 = pd.merge(df1, df_def[['Numer']], how='outer', on=['Numer'])
       
        df1['NR'] = df1['NR'].fillna(df1['Numer'])
        df2['NR'] = df2['NR'].fillna(df2['Numer'])

        df2 = df2.drop(columns=['Numer'])
        df1 = df1.drop(columns=['Numer'])

        self.df_1 = df1
        self.df_2 = df2

        self.setup_table(self.table1, self.df_1)
        self.setup_table(self.table2, self.df_2)

    def import_TXT(self):
        fname = QFileDialog.getOpenFileName(self, 'open file', os.path.expanduser("~/Desktop"), 'TXT File(*.txt)')
        if fname == ('', ''):
            return
        else:
            try:
                df = pd.DataFrame()
                df = pd.read_table(fname[0], sep= r'\s+', header=None, on_bad_lines='skip')
            except Exception as e:
                print(e)
        
        self.df_memory = self.table(df)
        self.status.setStyleSheet("background-color: #77C66E")

    def export_TXT(self):
        s_name = QFileDialog.getSaveFileName(self, 'select a file', os.path.expanduser("~/Desktop"),'Excel File(*.xlsx);;TXT File (*.txt);;TXT File With Tab Separator (*.txt);;CSV File (*.csv)')
        #print(s_name[0])
        #print(f'Name: {s_name[0]}')
        
        if s_name == ('', ''):
            return
        
        if self.df_1.empty and self.df_2.empty:
            print("Empty")
            return
        else:
            df = pd.concat([self.df_1, self.df_2, self.df_3], axis=1)
            
            df['X'] = df['X'].map('{:.2f}'.format)
            
            df['Y'] = df['Y'].map('{:.2f}'.format)
            
            try:
                df['H'] = df['H'].map('{:.2f}'.format)
            except:
                if 'H' not in df.columns or df['H'].empty:
                    try:
                        df.drop(columns='DH', inplace=True)
                    except:
                        pass

            if s_name[1] == "Excel File(*.xlsx)":
                df.to_excel(s_name[0], index=True)
            
            if s_name[1] == "TXT File (*.txt)":
                df.to_csv(s_name[0], index=False, sep=' ')

            elif s_name[1] == "TXT File With Tab Separator (*.txt)":
                df.to_csv(s_name[0], index=False, sep='\t')

            elif s_name[1] == "CSV File (*.csv)":
                df.to_csv(s_name[0], index=False)
            else:
                df.to_excel(s_name[0], index=True)

            print("Export")

    def oblicz(self):
        if self.df_1.empty or self.df_2.empty:
            print("Empty")
            return

        self.df_3 = self.oblicz_wsp(self.df_1, self.df_2)
        #print(self.df_3)
        self.setup_table(self.table3, self.df_3)

    def setup(self, table, path):
        for i in range(table.rowCount()):
            table.removeRow(0)

        df = pd.read_table(path, sep= r'\s+', header=None, on_bad_lines='skip')  # skip_blank_lines=True, skipinitialspace=True
        
        df = self.table(df)
        #print(df)
        if table.objectName() == "NR1":
            self.df_1 = df
            self.df_memory = df
            self.status.setStyleSheet("background-color: #77C66E")
        else:
            self.df_2 = df
        #print(self.df_1)
        for row_index, row_data in df.iterrows():
            table.insertRow(row_index)
            for col_index, col_value in enumerate(row_data):
                if col_index == 0:
                    try:
                        col_value = int(col_value)
                    except ValueError:
                        pass
                item = QTableWidgetItem(str(col_value))  # Convert value to string
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row_index, col_index, item)
        table.resizeColumnsToContents()

    def setup_table(self, table, df):
        for i in range(table.rowCount()):
            table.removeRow(0)
        for row_index, row_data in df.iterrows():
            table.insertRow(row_index)
            for col_index, col_value in enumerate(row_data):
                if col_index == 0:
                    try:
                        col_value = int(col_value)
                        item = QTableWidgetItem(str(col_value))
                    except:
                        item = QTableWidgetItem(str(col_value))
                        #print("col 1 number")
                else:
                    try:
                        col_value = float(col_value)
                        item = QTableWidgetItem("{:.2f}".format(col_value))
                        if df.columns[col_index] == 'DL' and col_value > 0.15:
                            item.setBackground(Qt.red)
                    except:
                        item = QTableWidgetItem(str(col_value))  # Convert value to string
                
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row_index, col_index, item)
        table.resizeColumnsToContents()

    def table(self, df):

        df = df.iloc[:,:4]

        df = self.rep(df)

        df, df_duplicates = self.is_duplicated(df)

        df = self.sort(df, "NR")

        df = df.iloc[:,:4]

        df.reset_index(drop=True, inplace=True)

        return df

    def separation(self):

        df = self.df_1

        if df.empty:
            print("Empty")
            return

        df_filtered_1 = df[~df['NR'].str.contains(r'[a-zA-Z]')]

        df_filtered_1 = df_filtered_1.sort_values(by='NR')
        df_filtered_1.reset_index(drop=True, inplace=True)

        df_filtered_2 = df[df['NR'].str.contains(r'[a-zA-Z]', regex=True)]

        df_filtered_2 = df_filtered_2.sort_values(by='NR')
        df_filtered_2.reset_index(drop=True, inplace=True)     

        self.df_1 = df_filtered_1
        self.df_2 = df_filtered_2

        self.setup_table(self.table1, self.df_1)
        self.setup_table(self.table2, self.df_2)
        return

    def oblicz_wsp(self, df1, df2):

        df_wsp = pd.DataFrame()

        df_wsp['DX'] = df2["X"] - df1["X"]
        
        df_wsp['DY'] = df2["Y"] - df1["Y"]
        

        try:
            df_wsp['DH'] = df2["H"] - df1["H"]
        except:
            df_wsp['DH'] = ""

        df_wsp['DL'] = (df_wsp['DX'] ** 2 + df_wsp['DY'] ** 2) ** 0.5
        df_wsp['DL'] = df_wsp['DL'].apply(lambda x: "{:.2f}".format(x))

        df_wsp['DX'] = df_wsp['DX'].apply(lambda x: "{:.2f}".format(x))
        df_wsp['DY'] = df_wsp['DY'].apply(lambda x: "{:.2f}".format(x))
        try:
            df_wsp['DH'] = df_wsp['DH'].apply(lambda x: "{:.2f}".format(x))
        except:
            df_wsp['DH'] = ""

        return df_wsp

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()  # Pobierz listę URL-ów przeciąganych plików
            for url in urls:
                
                if url.toLocalFile().endswith(".txt"):  # Sprawdź, czy rozszerzenie pliku to ".gml"
                    event.acceptProposedAction()
                    return       

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            mouse_pos = event.position().toPoint()  # Pobierz współrzędne myszy podczas upuszczania pliku
            target_table = None

            # Sprawdź, do której tabeli należy współrzędna myszy
            if self.table1.geometry().contains(mouse_pos):
                target_table = self.table1
            elif self.table2.geometry().contains(mouse_pos):
                target_table = self.table2

            if target_table is not None:
                #print(target_table)
                self.setup(target_table, file_path) #, target_table.objectName()

                print(f'Dropped GML file: {file_path} to table: {target_table.objectName()}')
                # Tutaj możesz przetworzyć plik i dodawać jego zawartość do wybranej tabeli
                # Przykładowo:
                # self.process_file(file_path, target_table)
                # self.add_file_contents_to_table(file_path, target_table)
            else:
                print(f'File dropped outside of any table.')

            #self.result_output("Offline.", "#686868")
   
    def dropsEvent(self, events):
        for url in events.mimeData().urls():
            file_path = url.toLocalFile()
            print(f'Dropped GML file: {file_path}')
            global Input_Path
            Input_Path = file_path

    def reset_table(self):
        self.df_1 = pd.DataFrame()
        self.df_2 = pd.DataFrame()
        self.df_3 = pd.DataFrame()
        self.df_memory = pd.DataFrame()
        self.df_list_1 = pd.DataFrame()
        self.df_list_2 = pd.DataFrame()
        print("reset")
        def tablereset(table):
            for i in range(table.rowCount()):
                table.removeRow(0)
        tablereset(self.table1)
        tablereset(self.table2)
        tablereset(self.table3)
        self.status.setStyleSheet("background-color: #ab2c0c")

    def run_sort(self, l_or_r, manual=False, name = None, Name_left_column = "Lista punktów:", Name_right_column = "Wybrane punkty:"):
        self.resize(1100,0)
        #self.setFixedWidth(1100)
        if not self.new_drag_drop_widget:
            self.new_drag_drop_widget = NewDragDropWidget(MainWindowP, self.df_memory, l_or_r, manual, self.df_1, self.df_2, name,  Name_left_column, Name_right_column)
            #self.new_drag_drop_widget = NewDragDropWidget(self.df_memory)
            self.dock_widget = QDockWidget()
            self.dock_widget.setWindowTitle("Porównanie współrzędnych.")
            self.dock_widget.setWidget(self.new_drag_drop_widget)
            #self.dock_widget.setWidget(self.new_drag_drop_widget)
            self.dock_widget.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
            self.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
            self.dock_widget.topLevelChanged.connect(self.on_dockLocationChanged)
            self.dock_widget.closeEvent = self.dockClosed
            self.dock_widget.raise_()

        else:
            self.new_drag_drop_widget = "True"
            self.dock_widget.close()
            self.run_sort(l_or_r = l_or_r, manual = manual, name = name, Name_left_column = Name_left_column, Name_right_column = Name_right_column)
        
        '''
        try:
            self.window = self.NewDragDropWidget()
            self.window.show()
        except Exception as e:
            print(e)
        '''

    def dockClosed(self, event):
        if not self.new_drag_drop_widget == "True":
            self.resize(500,0)
        self.new_drag_drop_widget = None
        #print(event)

    def on_dockLocationChanged(self, area):
        if area is True:
            #print("Window is dockable")
            self.resize(500,0)
        else:
            self.resize(1100,0)
            #print("Window is not dockable")
        #print(area)

    def closeEvent(self, event):
        try:
            print("Close")
        except AttributeError:
            return

    def sort(self, df, df_name):
        try:
            df['Rep'] = df[df_name].str.replace(r'[a-zA-Z]', '', regex=True)                
            df['SortN'] = df['Rep'].str.replace(r'[^a-zA-Z0-9]', '.', regex=True)
            df['SortL'] = df[df_name].str.replace(r'[^a-zA-Z]', '', regex=True)
            df.loc[df['SortN'] == '', 'SortN'] = np.nan    
            df['SortN'] = df['SortN'].astype(float)
            df = df.sort_values(['SortN', 'SortL'], na_position='first')
            #df = df.sort_values(['SortL', 'SortN'], na_position='first')
            df.drop(columns=['Rep', 'SortN', 'SortL'], axis=1, inplace=True)
            
            df.reset_index(drop=True, inplace=True)
        except Exception as e:
            #logging.exception(e)
            print(f'Sorting error {e}')
            #return
        return df

    def rep(self, df, df_N=0, df_X=1, df_Y=2, df_H=3):

        try:
            df[df_N] = df[df_N].astype(str)
            df = df.rename(columns = {df_N:'NR'})
        except Exception as e:
            #logging.exception(e)
            print(f'Sorting error {e}')
            #return
        try:
            
            df[df_X] = df[df_X].replace(',', '.', regex=True).astype(float)
            df[df_X] = df[df_X].map('{:.2f}'.format)
            df[df_X] = df[df_X].astype(float)
            df = df.rename(columns = {df_X:'X'})
            df[df_Y] = df[df_Y].replace(',', '.', regex=True).astype(float)
            df[df_Y] = df[df_Y].map('{:.2f}'.format)
            df[df_Y] = df[df_Y].astype(float)
            df = df.rename(columns = {df_Y:'Y'})
        except Exception as e:
            #logging.exception(e)
            print(f'Sorting error {e}')
            #return

        try:
            df[df_H] = df[df_H].replace(',', '.', regex=True).astype(float)
            df[df_H] = df[df_H].map('{:.2f}'.format)
            df[df_H] = df[df_H].astype(float)
            df = df.rename(columns = {df_H:'H'})
        except Exception as e:
            #logging.exception(e)
            print(f'Sorting error {e}')
            #return
        
        return df

    def is_duplicated(self, df):
        df_duplicates = df[df.duplicated(subset="NR", keep='first')].copy()
        
        df = df.drop_duplicates(subset="NR")
        
        return df, df_duplicates


    def open_edge(self):
        url = "https://www.paypal.com/donate/?hosted_button_id=DVJJ5QVHCN2X6"
        try:  # Spróbuj otworzyć w domyślnej przeglądarce
            webbrowser.open(url)
        except webbrowser.Error:  # Jeśli wystąpi błąd, np. brak dostępnej przeglądarki, otwórz w Edge
            edge_path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"  # Ścieżka do exe Edge'a na Windows, dostosuj ją do swojego środowiska
            webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path), 1)
            webbrowser.get('edge').open(url)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindowP = MyWindow()
    MainWindowP.show()
    sys.exit(app.exec())
