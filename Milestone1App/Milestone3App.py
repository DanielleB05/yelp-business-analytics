import sys
import psycopg2
from PyQt5 import QtWidgets, uic

Ui_MainWindow, QtBaseClass = uic.loadUiType("Milestone3.ui")

DB_CONFIG = {
    "dbname": "yelp_db",
    "user": "postgres",
    "password": "13105Ave_Db2305",
    "host": "localhost",
    "port": "5432"
};

class Milestone3App(QtBaseClass, Ui_MainWindow):
    def __init__(self):
        QtBaseClass.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Connect to yelp_db database
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()

        # Hide row numbers on all tables for visual preference
        self.businessTableWidget.verticalHeader().setVisible(False)
        self.topCategoriesTable.verticalHeader().setVisible(False)
        self.popularTableWidget.verticalHeader().setVisible(False)
        self.successfulTableWidget.verticalHeader().setVisible(False)

        # Make table widgets read-only so user cannot edit data
        self.topCategoriesTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.businessTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.popularTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.successfulTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # Make LineEdits read-only so user cannot edit zipcode data
        self.numBusinessesEdit.setReadOnly(True)
        self.populationEdit.setReadOnly(True)
        self.avgIncomeEdit.setReadOnly(True)

        # Load states on startup for state dropdown box
        self.load_states()

        # Connect UI signals to event handlers
        self.stateComboBox.currentTextChanged.connect(self.load_cities)
        self.cityListWidget.itemClicked.connect(self.load_zipcodes)
        self.zipcodeListWidget.itemClicked.connect(self.on_zipcode_selected)
        self.searchButton.clicked.connect(self.load_businesses)
        self.refreshButton.clicked.connect(self.load_popular_successful)
        self.clearButton.clicked.connect(self.clear_all)

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
        self.topCategoriesTable.setRowCount(0)
        self.popularTableWidget.setRowCount(0)
        self.successfulTableWidget.setRowCount(0)
        self.numBusinessesEdit.clear()
        self.populationEdit.clear()
        self.avgIncomeEdit.clear()
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
        self.topCategoriesTable.setRowCount(0)
        self.popularTableWidget.setRowCount(0)
        self.successfulTableWidget.setRowCount(0)
        self.numBusinessesEdit.clear()
        self.populationEdit.clear()
        self.avgIncomeEdit.clear()
        self.cursor.execute(
            """SELECT DISTINCT postal_code FROM business
               WHERE city = %s AND state = %s
               ORDER BY postal_code;""",
            (selected_city, selected_state)
        )

        for (zipcode,) in self.cursor.fetchall():
            self.zipcodeListWidget.addItem(zipcode)

    def on_zipcode_selected(self, zipcode_item):
        selected_zip = zipcode_item.text()
        self.load_zipcode_stats(selected_zip)
        self.load_top_categories(selected_zip)
        self.load_categories(selected_zip)
        self.businessTableWidget.setRowCount(0)
        self.popularTableWidget.setRowCount(0)
        self.successfulTableWidget.setRowCount(0)

    def load_zipcode_stats(self, selected_zip):
        # Number of business in zipcode
        self.cursor.execute(
            "SELECT COUNT(*) FROM business WHERE postal_code = %s;",
            (selected_zip,)
        )

        num_businesses = self.cursor.fetchone()[0]
        self.numBusinessesEdit.setText(str(num_businesses))

        # Population and average income from zipcodeData
        self.cursor.execute(
            "SELECT population, medianIncome FROM zipcodedata WHERE zipcode = %s;",
            (selected_zip,)
        )

        result = self.cursor.fetchone()

        # Fill population and average if results found, otherwise show N/A
        if result:
            population, median_income = result
            self.populationEdit.setText(str(population))
            self.avgIncomeEdit.setText(str(median_income))
        else:
            self.populationEdit.setText("N/A")
            self.avgIncomeEdit.setText("N/A")

    def load_top_categories(self, selected_zip):
        self.cursor.execute(
            """SELECT c.category_name, COUNT(b.business_id) AS num_businesses
               FROM category c
               JOIN business_category bc ON c.category_id = bc.category_id
               JOIN business b ON bc.business_id = b.business_id
               WHERE b.postal_code = %s
               GROUP BY c.category_name
               ORDER BY num_businesses DESC
               LIMIT 10;""",
            (selected_zip,)
        )

        results = self.cursor.fetchall()
        self.topCategoriesTable.setRowCount(len(results))

        # Populate the top categories table
        for row_idx, (category, count) in enumerate(results):
            self.topCategoriesTable.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(category)))
            self.topCategoriesTable.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(count)))

        self.topCategoriesTable.resizeColumnsToContents()

    def load_categories(self, selected_zip):
        self.categoryListWidget.clear()
        self.cursor.execute(
            """SELECT DISTINCT c.category_name
               FROM category c
               JOIN business_category bc ON c.category_id = bc.category_id
               JOIN business b ON bc.business_id = b.business_id
               WHERE b.postal_code = %s
               ORDER BY c.category_name;""",
            (selected_zip,)
        )

        # Add each category to list widget
        for (category,) in self.cursor.fetchall():
            self.categoryListWidget.addItem(category)

    def load_businesses(self):
        # Exit if no zipcode selected
        if not self.zipcodeListWidget.currentItem():
            return

        selected_zip = self.zipcodeListWidget.currentItem().text()

        selected_category = None

        # Get selected category if one is chosen
        if self.categoryListWidget.currentItem():
            selected_category = self.categoryListWidget.currentItem().text()

        # Query businesses by zipcode and category
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
            # Query all businesses in selected zipcode
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

        # Populate business table with query results
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

        # Adjust column widths for better readability
        total_width = self.businessTableWidget.width()
        self.businessTableWidget.setColumnWidth(0, int(total_width * 0.25))
        self.businessTableWidget.setColumnWidth(1, int(total_width * 0.20))
        self.businessTableWidget.setColumnWidth(2, int(total_width * 0.15))
        self.businessTableWidget.setColumnWidth(3, int(total_width * 0.08))
        self.businessTableWidget.setColumnWidth(4, int(total_width * 0.15))
        self.businessTableWidget.setColumnWidth(5, int(total_width * 0.12))
        self.businessTableWidget.setColumnWidth(6, int(total_width * 0.10))

    def load_popular_successful(self):
        print("Refresh clicked")
        print("Current zipcode item:", self.zipcodeListWidget.currentItem())
        if not self.zipcodeListWidget.currentItem():
            print("No zipcode selected, returning early")
            return
        selected_zip = self.zipcodeListWidget.currentItem().text()
        self.conn.commit()
        print("Selected zip:", selected_zip)

        if not self.zipcodeListWidget.currentItem():
            return

        selected_zip = self.zipcodeListWidget.currentItem().text()

        # Popular businesses
        self.cursor.execute(
            """SELECT DISTINCT b.name, b.num_checkins, avg_ci.avg_checkins
               FROM business b
               JOIN business_category bc ON b.business_id = bc.business_id
               JOIN (
                   SELECT bc2.category_id, b2.postal_code,
                          AVG(b2.num_checkins) AS avg_checkins
                   FROM business b2
                   JOIN business_category bc2 ON b2.business_id = bc2.business_id
                   GROUP BY bc2.category_id, b2.postal_code
               ) avg_ci ON bc.category_id = avg_ci.category_id
                        AND b.postal_code = avg_ci.postal_code
               WHERE b.postal_code = %s
                 AND b.num_checkins > avg_ci.avg_checkins * 1.5
               ORDER BY b.num_checkins DESC;""",
            (selected_zip,)
        )

        popular = self.cursor.fetchall()
        self.popularTableWidget.setRowCount(len(popular))

        for row_idx, (name, checkins, avg_checkins) in enumerate(popular):
            name_item = QtWidgets.QTableWidgetItem(str(name))
            name_item.setToolTip(str(name))
            self.popularTableWidget.setItem(row_idx, 0, name_item)
            self.popularTableWidget.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(checkins)))
            self.popularTableWidget.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(str(round(float(avg_checkins), 2))))

        self.popularTableWidget.resizeColumnsToContents()

        # Successful businesses
        self.cursor.execute(
            """SELECT b.name, b.avg_review_rating, b.review_count, b.num_checkins,
                  ROUND((
                      (b.avg_review_rating * 0.5) +
                      (LOG(b.review_count + 1) * 0.3) +
                      (LOG(b.num_checkins + 1) * 0.2)
                  )::numeric, 4) AS success_score
               FROM business b
               WHERE b.postal_code = %s
                 AND b.is_open = 1
                 AND b.avg_review_rating >= 3.5
                 AND b.review_count >= 10
               ORDER BY success_score DESC;""",
            (selected_zip,)
        )

        successful = self.cursor.fetchall()
        self.successfulTableWidget.setRowCount(len(successful))

        for row_idx, (name, avg_rating, review_count, checkins, score) in enumerate(successful):
            name_item = QtWidgets.QTableWidgetItem(str(name))
            name_item.setToolTip(str(name))
            self.successfulTableWidget.setItem(row_idx, 0, name_item)
            self.successfulTableWidget.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(avg_rating)))
            self.successfulTableWidget.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(str(review_count)))
            self.successfulTableWidget.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(str(checkins)))
            self.successfulTableWidget.setItem(row_idx, 4, QtWidgets.QTableWidgetItem(str(score)))

        self.successfulTableWidget.resizeColumnsToContents()
        
    # Enable ability to clear all entered data prior to loading popular/successful businesses
    def clear_all(self):
        self.cityListWidget.clear()
        self.zipcodeListWidget.clear()
        self.categoryListWidget.clear()
        self.businessTableWidget.setRowCount(0)
        self.topCategoriesTable.setRowCount(0)
        self.numBusinessesEdit.clear()
        self.populationEdit.clear()
        self.avgIncomeEdit.clear()
        self.stateComboBox.setCurrentIndex(0)

# Create and run main application window
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Milestone3App()
    window.show()
    sys.exit(app.exec_())