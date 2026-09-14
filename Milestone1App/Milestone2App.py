import sys
import psycopg2
from PyQt5 import QtWidgets, uic

Ui_MainWindow, QtBaseClass = uic.loadUiType("Milestone2.ui")

DB_CONFIG = {
    "dbname": "yelp_db",
    "user": "postgres",
    "password": "13105Ave_Db2305",
    "host": "localhost",
    "port": "5432"
}


class Milestone2App(QtBaseClass, Ui_MainWindow):
    def __init__(self):
        QtBaseClass.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Connect to yelp_db
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()

        # Hide row numbers on the business table
        self.businessTableWidget.verticalHeader().setVisible(False)

        # Load states immediately on startup
        self.load_states()

        # Wire up signals
        self.stateComboBox.currentTextChanged.connect(self.load_cities)
        self.cityListWidget.itemClicked.connect(self.load_zipcodes)
        self.zipcodeListWidget.itemClicked.connect(self.load_categories)
        self.searchButton.clicked.connect(self.load_businesses)

    def load_states(self):
        self.cursor.execute(
            "SELECT DISTINCT state FROM business ORDER BY state;"
        )

        for (state,) in self.cursor.fetchall():
            self.stateComboBox.addItem(state)

    def load_cities(self, selected_state):
        self.cityListWidget.clear()
        self.zipcodeListWidget.clear()
        self.categoryListWidget.clear()
        self.businessTableWidget.setRowCount(0)
        self.cursor.execute(
            "SELECT DISTINCT city FROM business WHERE state = %s ORDER BY city;",
            (selected_state,)
        )

        for (city,) in self.cursor.fetchall():
            self.cityListWidget.addItem(city)

    def load_zipcodes(self, city_item):
        selected_city = city_item.text()
        selected_state = self.stateComboBox.currentText()
        self.zipcodeListWidget.clear()
        self.categoryListWidget.clear()
        self.businessTableWidget.setRowCount(0)
        self.cursor.execute(
            """SELECT DISTINCT postal_code FROM business
               WHERE city = %s AND state = %s
               ORDER BY postal_code;""",
            (selected_city, selected_state)
        )

        for (zipcode,) in self.cursor.fetchall():
            self.zipcodeListWidget.addItem(zipcode)

    def load_categories(self, zipcode_item):
        selected_zip = zipcode_item.text()
        self.categoryListWidget.clear()
        self.businessTableWidget.setRowCount(0)
        self.cursor.execute(
            """SELECT DISTINCT c.category_name
               FROM category c
               JOIN business_category bc ON c.category_id = bc.category_id
               JOIN business b ON bc.business_id = b.business_id
               WHERE b.postal_code = %s
               ORDER BY c.category_name;""",
            (selected_zip,)
        )

        for (category,) in self.cursor.fetchall():
            self.categoryListWidget.addItem(category)

    def load_businesses(self):

        if not self.zipcodeListWidget.currentItem():
            return

        selected_zip = self.zipcodeListWidget.currentItem().text()

        # Check if user also selected a category to filter by
        selected_category = None

        if self.categoryListWidget.currentItem():
            selected_category = self.categoryListWidget.currentItem().text()

        if selected_category:
            self.cursor.execute(
                """SELECT DISTINCT b.name, b.address, b.city, b.stars,
                          b.review_count, b.avg_review_rating, b.num_checkins
                   FROM business b
                   JOIN business_category bc ON b.business_id = bc.business_id
                   JOIN category c ON bc.category_id = c.category_id
                   WHERE b.postal_code = %s AND c.category_name = %s
                   ORDER BY b.name;""",
                (selected_zip, selected_category)
            )
        else:
            self.cursor.execute(
                """SELECT b.name, b.address, b.city, b.stars,
                          b.review_count, b.avg_review_rating, b.num_checkins
                   FROM business b
                   WHERE b.postal_code = %s
                   ORDER BY b.name;""",
                (selected_zip,)
            )

        businesses = self.cursor.fetchall()
        self.businessTableWidget.setRowCount(len(businesses))

        for row_idx, (name, address, city, stars, review_count, avg_rating, checkins) in enumerate(businesses):
            name_item = QtWidgets.QTableWidgetItem(str(name))
            name_item.setToolTip(str(name))
            self.businessTableWidget.setItem(row_idx, 0, name_item)
            address_item = QtWidgets.QTableWidgetItem(str(address))
            address_item.setToolTip(str(address))
            self.businessTableWidget.setItem(row_idx, 1, address_item)
            self.businessTableWidget.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(str(city)))
            self.businessTableWidget.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(str(stars)))
            self.businessTableWidget.setItem(row_idx, 4, QtWidgets.QTableWidgetItem(str(review_count)))
            self.businessTableWidget.setItem(row_idx, 5, QtWidgets.QTableWidgetItem(str(avg_rating)))
            self.businessTableWidget.setItem(row_idx, 6, QtWidgets.QTableWidgetItem(str(checkins)))

        total_width = self.businessTableWidget.width()
        self.businessTableWidget.setColumnWidth(0, int(total_width * 0.20))  # Name
        self.businessTableWidget.setColumnWidth(1, int(total_width * 0.20))  # Address
        self.businessTableWidget.setColumnWidth(2, int(total_width * 0.15))  # City
        self.businessTableWidget.setColumnWidth(3, int(total_width * 0.08))  # Stars
        self.businessTableWidget.setColumnWidth(4, int(total_width * 0.15))  # Review Count
        self.businessTableWidget.setColumnWidth(5, int(total_width * 0.12))  # Avg Rating
        self.businessTableWidget.setColumnWidth(6, int(total_width * 0.10))  # Checkins

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Milestone2App()
    window.show()
    sys.exit(app.exec_())