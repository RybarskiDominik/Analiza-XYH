import sys
from PySide6.QtWidgets import QApplication, QListWidget
from PySide6.QtCore import Qt, QSize
from PySide6 import QtCore, QtWidgets
import pandas as pd

import re

class NewDragDropWidget(QtWidgets.QMainWindow):
    def __init__(self, MainWindowP=None,
                memory=pd.DataFrame(),
                l_or_r=None,
                manual=False,
                df1=pd.DataFrame(),
                df2=pd.DataFrame(),
                column_name = "NR",
                Name_left_column = "Lista punktów:",
                Name_right_column = "Wybrane punkty:"):
        super().__init__()
        self.df_export = pd.DataFrame()
        self.df_memory = memory
        self.manual = manual
        self.list1 = pd.DataFrame()
        self.list2 = pd.DataFrame()

        self.df1 = df1
        self.df2 = df2

        self.MainWindowP = MainWindowP

        self.setWindowTitle("Porównanie współrzędnych.")
        #self.setAcceptDrops(True)

        self.main_widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QHBoxLayout()
        self.verticallayout = QtWidgets.QVBoxLayout()
        self.gridlayout = QtWidgets.QGridLayout()

        self.listWidgetLeft = QtWidgets.QListWidget()  # QListWidget()
        self.listWidgetLeft.setGeometry(0, 2, 100, 400)
        self.listWidgetLeft.setSortingEnabled(True)
        self.listWidgetLeft.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.listWidgetLeft.setSelectionMode(QListWidget.ExtendedSelection)
        self.listWidgetLeft.doubleClicked.connect(self.on_double_clicked_to_right)
        #self.listWidgetLeft.show()
        #self.listWidgetLeft.setDragEnabled(True)

        self.listWidgetRight = QtWidgets.QListWidget()  # QListWidget()
        self.listWidgetRight.setGeometry(100, 22, 100, 400)
        self.listWidgetRight.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        #self.listWidgetRight.setDragDropOverwriteMode(False)
        self.listWidgetRight.setSelectionMode(QListWidget.ExtendedSelection)
        self.listWidgetRight.doubleClicked.connect(self.on_double_clicked_to_left)
        #self.listWidgetRight.setDragEnabled(True)

        self.list_Item_left = QtWidgets.QLineEdit()
        self.list_Item_left.setText(Name_left_column)
        self.list_Item_left.setReadOnly(True)

        self.sortleft = QtWidgets.QPushButton()
        self.sortleft.setText("Sort")
        self.sortleft.setMaximumSize(QSize(32, 32))
        self.sortleft.clicked.connect(self.sort_left_list)

        self.list_Item_right = QtWidgets.QLineEdit()
        self.list_Item_right.setText(Name_right_column)
        self.list_Item_right.setReadOnly(True)

        self.sortright = QtWidgets.QPushButton()
        self.sortright.setText("Sort")
        self.sortright.setMaximumSize(QSize(30, 30))
        self.sortright.clicked.connect(self.sort_right_list)
        
        self.buttonok = QtWidgets.QPushButton()
        self.buttonok.setText("OK")
        self.buttonok.clicked.connect(lambda: self.export(l_or_r, manual))

        self.buttoncancel = QtWidgets.QPushButton()
        self.buttoncancel.setText("Anuluj")
        self.buttoncancel.clicked.connect(self.closeEvent)

        self.clear = QtWidgets.QPushButton()
        self.clear.setText("Wyczyść")
        self.clear.setGeometry(0, 20, 95, 28)
        self.clear.clicked.connect(self.clear_list)

        self.add_L = QtWidgets.QPushButton()
        self.add_L.setText("<")
        self.add_L.setMaximumSize(QSize(30, 30))
        self.add_L.clicked.connect(self.add_selected_to_left)

        self.add_R = QtWidgets.QPushButton()
        self.add_R.setText(">")
        self.add_R.setMaximumSize(QSize(30, 30))
        self.add_R.clicked.connect(self.add_selected_to_right)


        self.all_R = QtWidgets.QPushButton()
        self.all_R.setText(">>")
        self.all_R.setMaximumSize(QSize(30, 30))
        self.all_R.clicked.connect(self.all_to_right)

        self.all_L = QtWidgets.QPushButton()
        self.all_L.setText("<<")
        self.all_L.setMaximumSize(QSize(30, 30))
        self.all_L.clicked.connect(self.all_to_left)

        self.custom_sort = QtWidgets.QLineEdit()
        self.custom_sort.setMaxLength(1)
        self.custom_sort.setAlignment(QtCore.Qt.AlignCenter)
        self.custom_sort.setPlaceholderText("*")
        self.custom_sort.setMaximumSize(QSize(26, 26))
        self.custom_sort.textChanged.connect(self.custom_sort_list)
        self.custom_sort.setToolTip("Sortowanie")

        self.initUI()
        self.start(column_name, manual)

    def initUI(self):

        self.layoutsort1 = QtWidgets.QHBoxLayout()
        self.layoutsort1.addWidget(self.list_Item_left)
        self.layoutsort1.addWidget(self.sortleft, alignment=Qt.AlignTop)
        self.gridlayout.addLayout(self.layoutsort1, 0, 0, 1, 1,)
        self.gridlayout.addWidget(self.listWidgetLeft, 1, 0, 1, 1)
        self.gridlayout.setSpacing(0)

        '''
        self.layout.addWidget(self.del_Item, alignment=Qt.AlignTop)
        self.layout.addWidget(self.clear, alignment=Qt.AlignTop)
        self.layout.addWidget(self.add_L, alignment=Qt.AlignTop)
        self.layout.addWidget(self.all_L, alignment=Qt.AlignTop)
        self.layout.addWidget(self.add_R, alignment=Qt.AlignTop)
        self.layout.addWidget(self.all_R, alignment=Qt.AlignTop)
        '''

        self.verticallayout.addWidget(self.add_R, alignment=Qt.AlignTop)
        self.verticallayout.addWidget(self.all_R, alignment=Qt.AlignTop)
        self.verticallayout.addWidget(self.add_L, alignment=Qt.AlignTop)
        self.verticallayout.addWidget(self.all_L, alignment=Qt.AlignTop)
        self.verticallayout.addWidget(self.custom_sort, alignment=Qt.AlignCenter)
        self.verticallayout.setSpacing(5)
        self.verticallayout.addStretch(1)

        self.layoutsort2 = QtWidgets.QHBoxLayout()
        self.layoutsort2.addWidget(self.list_Item_right)
        self.layoutsort2.addWidget(self.sortright, alignment=Qt.AlignTop)
        self.gridlayout.addLayout(self.layoutsort2, 0, 3, 1, 1,)

        self.gridlayout.addWidget(self.listWidgetRight, 1, 3, 1, 1)
        self.gridlayout.addLayout(self.verticallayout, 1, 2, 1, 1)
        
        self.layoutsort3 = QtWidgets.QHBoxLayout()
        self.layoutsort3.addWidget(self.buttonok)
        self.layoutsort3.addWidget(self.buttoncancel)
        self.gridlayout.addLayout(self.layoutsort3, 3, 3, 1, 1,)

        self.main_widget.setLayout(self.gridlayout)

        self.setCentralWidget(self.main_widget)
        
        self.setMinimumSize(200, 300)
        self.setFixedSize(400, 400)
        
        window_width = 250
        window_height = 300

        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        self.setGeometry(x, y, window_width, window_height)
        self.show()

    def start(self, column_name, manual):
        if manual == False:
            if self.df_memory.empty:
                self.df_memory = pd.DataFrame({column_name: ['Import TXT', 'Import TXT', 'Import TXT', 'Import TXT', 'Import TXT', 'Import TXT']})
                for index, row in self.df_memory.iterrows():
                    self.listWidgetLeft.addItem(row[column_name])
            else:
                try:
                    for index, row in self.df_memory.iterrows():
                            self.listWidgetLeft.addItem(row[column_name])
                except Exception as e:
                    #logging.exception(e)
                    print(e)
        else:
            try:
                for index, row in self.df1.iterrows():
                    self.listWidgetLeft.addItem(row[column_name])           
            except Exception as e:
                #logging.exception(e)
                print(e)
            try:           
                for index, row in self.df2.iterrows():
                    self.listWidgetRight.addItem(row[column_name])
            except Exception as e:
                #logging.exception(e)
                print(e)

            #print('manual True')

    def export(self, l_or_r, manual):
        self.df_export = pd.DataFrame()
        self.df_export_two = pd.DataFrame()
        if manual == False:
            if l_or_r == "L":
                for i in range(self.listWidgetRight.count()):
                    item = self.listWidgetRight.item(i)
                    self.df_export = pd.concat([self.df_export, pd.DataFrame({'Sorted': [item.text()]})], ignore_index=True)
                
                self.MainWindowP.df_list_1 = self.df_export                
                self.MainWindowP.synchronize("L")
                
                print("L")
            elif l_or_r == "R":
                for i  in range(self.listWidgetRight.count()):
                    item = self.listWidgetRight.item(i)
                    self.df_export = pd.concat([self.df_export, pd.DataFrame({'Sorted': [item.text()]})], ignore_index=True)
                
                self.MainWindowP.df_list_2 = self.df_export                
                self.MainWindowP.synchronize("R")
                
            else:
                print("pass")
                #return
            #MyWindow.synchronize(MainWindowP)
        else:
            try:
                for i in range(self.listWidgetLeft.count()):
                    item = self.listWidgetLeft.item(i)
                    self.df_export = pd.concat([self.df_export, pd.DataFrame({'Sorted': [item.text()]})], ignore_index=True)
                #print(self.df_export)
                self.MainWindowP.df_list_1 = self.df_export                
                
            except Exception as e:
                #logging.exception(e)
                print(e)

            try:
                for i  in range(self.listWidgetRight.count()):
                    item = self.listWidgetRight.item(i)
                    self.df_export_two = pd.concat([self.df_export_two, pd.DataFrame({'Sorted': [item.text()]})], ignore_index=True)
                #print(self.df_export_two)
                self.MainWindowP.df_list_2 = self.df_export_two                
                
            except Exception as e:
                #logging.exception(e)
                print(e)
            self.MainWindowP.synchronize_manual()
            print("Manual True")

    def add_selected_to_left(self):
        selected_items = self.listWidgetRight.selectedItems()
        for item in selected_items:
            self.listWidgetLeft.addItem(item.text())
            self.listWidgetRight.takeItem(self.listWidgetRight.row(item))

    def add_selected_to_right(self):
        selected_items = self.listWidgetLeft.selectedItems()
        for item in selected_items:
            self.listWidgetRight.addItem(item.text())
            self.listWidgetLeft.takeItem(self.listWidgetLeft.row(item))
    
    def all_to_right(self):
        for i in range(self.listWidgetLeft.count()):
            self.listWidgetRight.addItem(self.listWidgetLeft.takeItem(0))

    def all_to_left(self):
        for i in range(self.listWidgetRight.count()):
            self.listWidgetLeft.addItem(self.listWidgetRight.takeItem(0))

    def delete_item(self):
        listItems = self.listWidgetRight.selectedItems()
        if not listItems:
            self.listWidgetRight.setCurrentItem(self.listWidgetRight.item(0))
            if self.listWidgetRight.count() > 0:
                self.delete_item()
        for item in listItems:
            self.listWidgetRight.takeItem(self.listWidgetRight.row(item))

    def clear_list(self):
        self.listWidgetRight.setCurrentItem(self.listWidgetRight.item(0))
        for i in range(self.listWidgetRight.count()):
            self.listWidgetRight.clear()

    def on_double_clicked_to_right(self):
        row = self.listWidgetLeft.currentRow()
        rowItem = self.listWidgetLeft.takeItem(row)
        self.listWidgetRight.addItem(rowItem)

    def on_double_clicked_to_left(self):
        row = self.listWidgetRight.currentRow()
        rowItem = self.listWidgetRight.takeItem(row)
        self.listWidgetLeft.addItem(rowItem)

    def sort_left_list(self):
        self.listWidgetLeft.sortItems()
        print('L')

    def sort_right_list(self):
        self.listWidgetRight.sortItems()
        print('R')

    def closeEvent(self, event):
        try:
            self.MainWindowP.dock_widget.close()
        except Exception as e:
            #logging.exception(e)
            print(e)
        
        self.close()
        print("Close")

    def custom_sort_list(self):
        sort_value = self.custom_sort.text()
        item_count = self.listWidgetLeft.count()
        if sort_value != '':
            pattern = re.compile(re.escape(sort_value), re.IGNORECASE)  # Create a regular expression pattern with wildcard and ignore case
            for i in range(item_count):
                item = self.listWidgetLeft.item(i)
                if not re.search(pattern, item.text()):  # Check if sort_value is not found in item.text()
                    item.setHidden(True)
        else:
            item_count = self.listWidgetLeft.count()
            for i in range(item_count):
                item = self.listWidgetLeft.item(i)
                item.setHidden(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = NewDragDropWidget()
    window.show()
    sys.exit(app.exec())
