import sys
import psycopg2
from PyQt5 import QtWidgets, uic

Ui_MainWindow, QtBaseClass = uic.loadUiType("MainWindow.ui")

class MyApp(QtBaseClass, Ui_MainWindow):
    def __init__(self):
        QtBaseClass.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.businessTableWidget.verticalHeader().setVisible(False)

        # Connect to PostgreSQL
        self.conn = psycopg2.connect(
            dbname="milestone1db",
            user="postgres",
            password="13105Ave_Db2305",
            host="localhost",
            port="5432"
        )

        self.cursor = self.conn.cursor()

        # Populate the state dropdown right away
        self.load_states()

        # When user picks something, run handler
        self.stateComboBox.currentTextChanged.connect(self.load_cities)
        self.cityListWidget.itemClicked.connect(self.load_businesses)

    # Load the states from the data
    def load_states(self):
        self.cursor.execute("SELECT DISTINCT state FROM business ORDER BY state;")
        states = self.cursor.fetchall()
        
        for (state,) in states:
            self.stateComboBox.addItem(state)

    # Load the cities from the data
    def load_cities(self, selected_state):
        self.cityListWidget.clear()
        self.businessTableWidget.setRowCount(0)
        self.cursor.execute(
            "SELECT DISTINCT city FROM business WHERE state = %s ORDER BY city;",
            (selected_state,)
        )
        
        cities = self.cursor.fetchall()
        for (city,) in cities:
            self.cityListWidget.addItem(city)

    # Load the businesses from the data
    def load_businesses(self, city_item):
        selected_city = city_item.text()
        selected_state = self.stateComboBox.currentText()

        self.cursor.execute(
            "SELECT name, city, state FROM business WHERE city = %s AND state = %s ORDER BY name;",
            (selected_city, selected_state)
        )

        # Adjust table widget for 3 columns
        businesses = self.cursor.fetchall()
        self.businessTableWidget.setRowCount(len(businesses))
        for row_index, (name, city, state) in enumerate(businesses):
            self.businessTableWidget.setItem(row_index, 0, QtWidgets.QTableWidgetItem(name))
            self.businessTableWidget.setItem(row_index, 1, QtWidgets.QTableWidgetItem(city))
            self.businessTableWidget.setItem(row_index, 2, QtWidgets.QTableWidgetItem(state))

        # Adjust table widget to properly fit name, city, and state columns
        header = self.businessTableWidget.horizontalHeader()
        header.setStretchLastSection(False)
        total_width = self.businessTableWidget.width()
        self.businessTableWidget.setColumnWidth(0, int(total_width * 0.6))
        self.businessTableWidget.setColumnWidth(1, int(total_width * 0.2))
        self.businessTableWidget.setColumnWidth(2, int(total_width * 0.2))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())