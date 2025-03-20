from giaodienchinh import Ui_MainWindow
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QHeaderView, QAbstractItemView
from PyQt6 import QtCore
from PyQt6.QtCore import QDateTime
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime, timedelta

# MongoDB Connection
client = MongoClient('mongodb+srv://nhatnak24406:Mehellome!123@for-hkii-anhnhat.a26uk.mongodb.net/?retryWrites=true&w=majority&appName=for-HKII-AnhNhat')
db = client["finalproject"]
collection = db["products_data"]
class NhapKho(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        # Kết nối sự kiện click vào ô trong bảng thông báo
        self.tableWidget.cellClicked.connect(self.on_table_item_clicked)

        # Kết nối sự kiện cho nút xóa thông báo
        self.pushButton_3.clicked.connect(self.delete_selected_warning)
        self.pushButton_4.clicked.connect(self.delete_all_warnings)

        # Kiểm tra kho và hiển thị cảnh báo khi khởi động
        self.check_stock()
        self.check_expiration_dates()

        self.tableWidget.cellClicked.connect(self.on_table_item_clicked)
        self.pushButton_3.clicked.connect(self.delete_selected_warning)
        self.pushButton_4.clicked.connect(self.delete_all_warnings)
        self.check_stock()
        self.check_expiration_dates()

        # Add new code for category filters
        self.radioButton.clicked.connect(lambda: self.filter_by_category("Thực phẩm"))
        self.radioButton_2.clicked.connect(lambda: self.filter_by_category("Đồ gia dụng"))
        self.radioButton_3.clicked.connect(lambda: self.filter_by_category("Văn phòng phẩm"))

        # Initialize the header and format of the product list table
        self.tblDanhSach.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.btnNhapKho.clicked.connect(self.nhap_kho)
        self.btnNhapKho_2.clicked.connect(self.xoa_du_lieu_nhap)

        # Add input event handlers for product ID and name
        self.QtblXuatThongTin_3.cellChanged.connect(self.check_existing_product)

        # Initialize tables
        self.setup_tables()


#%% - tab1
    def check_stock(self):
        # Xóa bảng hiện tại
        self.tableWidget.setRowCount(0)

        # Truy vấn tất cả sản phẩm từ database
        products = collection.find()

        # Duyệt qua từng sản phẩm và kiểm tra số lượng
        for product in products:
            min_stock = product.get('MinimumStock', 0)
            if product.get('Quantity', 0) < min_stock:
                self.show_warning(product, "stock")

    def check_expiration_dates(self):
        # Lấy ngày hiện tại
        current_date = datetime.now()

        # Truy vấn tất cả sản phẩm từ database
        products = collection.find()

        # Duyệt qua từng sản phẩm và kiểm tra ngày hết hạn
        for product in products:
            expiration_date_str = product.get('ExpirationDate')

            if expiration_date_str:
                try:
                    # Chuyển đổi chuỗi ngày thành đối tượng datetime
                    # Điều chỉnh định dạng tùy theo cách lưu trữ trong MongoDB
                    # Giả sử định dạng là 'YYYY-MM-DD'
                    expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d')

                    # Tính số ngày còn lại đến khi hết hạn
                    days_remaining = (expiration_date - current_date).days

                    # Nếu còn ít hơn 31 ngày đến hạn sử dụng
                    if 0 < days_remaining <= 31:
                        # Thêm thông tin số ngày còn lại vào sản phẩm
                        product['days_remaining'] = days_remaining
                        self.show_warning(product, "expiration")
                except (ValueError, TypeError):
                    # Xử lý lỗi nếu định dạng ngày không đúng
                    continue

    def show_warning(self, product, warning_type):
        # Thêm thông báo vào bảng thông báo chung
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)

        # Tạo item với nội dung cảnh báo
        if warning_type == "stock":
            warning_text = "Cảnh báo sắp hết hàng"
        else:  # warning_type == "expiration"
            warning_text = "Cảnh báo sắp hết hạn sử dụng"

        warning_item = QTableWidgetItem(warning_text)

        # Lưu ID sản phẩm và loại cảnh báo vào item để dễ dàng truy xuất sau này
        warning_item.setData(QtCore.Qt.ItemDataRole.UserRole, str(product['_id']))
        warning_item.setData(QtCore.Qt.ItemDataRole.UserRole + 1, warning_type)

        # Đặt item vào bảng
        self.tableWidget.setItem(row_position, 0, warning_item)

    def on_table_item_clicked(self, row, column):
        # Lấy item đã click
        item = self.tableWidget.item(row, 0)

        if item:
            # Lấy ID sản phẩm từ dữ liệu UserRole
            product_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
            warning_type = item.data(QtCore.Qt.ItemDataRole.UserRole + 1)

            if product_id:
                # Tìm sản phẩm trong MongoDB
                product = collection.find_one({"_id": ObjectId(product_id)})

                if product:
                    # Xác định nội dung thông báo dựa vào loại cảnh báo
                    if warning_type == "stock":
                        warning_message = f"Mặt hàng {product.get('Name', 'N/A')} sắp hết và còn {product.get('Quantity', 0)} sản phẩm, vui lòng nhập hàng mới"
                    else:  # warning_type == "expiration"
                        days_remaining = product.get('days_remaining', 0)
                        warning_message = f"Mặt hàng {product.get('Name', 'N/A')} sắp hết hạn sử dụng (hạn sử dụng còn lại dưới 30 ngày), vui lòng kiểm tra lại"

                    # Hiển thị thông báo chi tiết
                    self.plnHienThongBao.setPlainText(warning_message)

                    # Cập nhật thông tin vào bảng chi tiết
                    self.QtblXuatThongTin_5.setItem(0, 0, QTableWidgetItem(str(product.get('ProductID', 'N/A'))))
                    self.QtblXuatThongTin_5.setItem(1, 0, QTableWidgetItem(product.get('Name', 'N/A')))
                    self.QtblXuatThongTin_5.setItem(2, 0, QTableWidgetItem(product.get('Category', 'N/A')))
                    self.QtblXuatThongTin_5.setItem(3, 0, QTableWidgetItem(str(product.get('UnitPrice', 'N/A'))))
                    self.QtblXuatThongTin_5.setItem(4, 0, QTableWidgetItem(str(product.get('Quantity', 'N/A'))))
                    self.QtblXuatThongTin_5.setItem(5, 0, QTableWidgetItem(
                        'Còn hàng' if product.get('Quantity', 0) > 0 else 'Hết hàng'))
                    self.QtblXuatThongTin_5.setItem(6, 0, QTableWidgetItem(str(product.get('DateInStock', 'N/A'))))
                    self.QtblXuatThongTin_5.setItem(7, 0, QTableWidgetItem(str(product.get('ExpirationDate', 'N/A'))))
                    self.QtblXuatThongTin_5.setItem(8, 0, QTableWidgetItem(str(product.get('MinimumStock', 'N/A'))))
                    self.QtblXuatThongTin_5.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def delete_selected_warning(self):
        # Xóa thông báo được chọn
        selected_rows = self.tableWidget.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            self.tableWidget.removeRow(row)
            self.plnHienThongBao.clear()
            # Xóa nội dung bảng thông tin sản phẩm
            for i in range(9):
                self.QtblXuatThongTin_5.setItem(i, 0, QTableWidgetItem(""))

    def delete_all_warnings(self):
        # Xóa tất cả thông báo
        self.tableWidget.setRowCount(0)
        self.plnHienThongBao.clear()
        # Xóa nội dung bảng thông tin sản phẩm
        for i in range(9):
            self.QtblXuatThongTin_5.setItem(i, 0, QTableWidgetItem(""))

#%% - tab2
    def filter_by_category(self, category):
        # Clear existing rows
        self.tblDanhSach.setRowCount(0)

        # Query products by category from database
        products = collection.find({"Category": category})

        # Display products in the table
        for row_idx, product in enumerate(products):
            self.tblDanhSach.insertRow(row_idx)

            # Set data for each column according to column names
            self.tblDanhSach.setItem(row_idx, 0, QTableWidgetItem(str(product.get('ProductID', ''))))
            self.tblDanhSach.setItem(row_idx, 1, QTableWidgetItem(product.get('Name', '')))
            self.tblDanhSach.setItem(row_idx, 2, QTableWidgetItem(str(product.get('UnitPrice', ''))))
            self.tblDanhSach.setItem(row_idx, 3, QTableWidgetItem(str(product.get('Quantity', ''))))
            self.tblDanhSach.setItem(row_idx, 4, QTableWidgetItem(str(product.get('ImportDate', ''))))
            self.tblDanhSach.setItem(row_idx, 5, QTableWidgetItem(str(product.get('ExpirationDate', ''))))

            # Determine product status
            status = 'Còn hàng' if product.get('Quantity', 0) > 0 else 'Hết hàng'
            self.tblDanhSach.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

            self.tblDanhSach.setItem(row_idx, 6, QTableWidgetItem(status))

#%% - tab3
    def setup_tables(self):
        """Setup tables with appropriate configuration"""
        # Make sure the QtblXuatThongTin_3 is editable
        for row in range(self.QtblXuatThongTin_3.rowCount()):
            # Create editable items for each row
            editable_item = QTableWidgetItem("")
            self.QtblXuatThongTin_3.setItem(row, 0, editable_item)

        # Make the product info table read-only
        self.QtblXuatThongTin_4.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Set current date as default for import date
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.QtblXuatThongTin_3.item(5, 0).setText(current_date)

    def check_existing_product(self, row, column):
        """Check if product ID or name already exists in MongoDB"""
        if column == 0 and (row == 0 or row == 1):  # Product ID or Product Name row
            value = self.QtblXuatThongTin_3.item(row, column).text().strip()
            if not value:
                return

            # Define search query based on row (0=ID, 1=Name)
            search_field = "ProductID" if row == 0 else "Name"
            query = {search_field: value}

            # Search in MongoDB
            existing_product = collection.find_one(query)

            if existing_product:
                # Product found, fill in the other fields
                self.fill_product_details(existing_product)
                # Show details in the info table
                self.display_product_info(existing_product)

    def fill_product_details(self, product_data):
        """Fill the input table with existing product details"""
        # Map MongoDB fields to table rows
        field_mapping = {
            "ProductID": 0,
            "Name": 1,
            "Category": 2,
            "UnitPrice": 3,
            "Status": 8
        }

        # Fill in the data for non-editable fields (except Quantity, ImportDate, ExpirationDate)
        for field, row in field_mapping.items():
            if field in product_data:
                value = str(product_data[field])
                if self.QtblXuatThongTin_3.item(row, 0) is None:
                    self.QtblXuatThongTin_3.setItem(row, 0, QTableWidgetItem(value))
                else:
                    self.QtblXuatThongTin_3.item(row, 0).setText(value)

        # Set MinimumStock
        if "MinimumStock" in product_data:
            value = str(product_data["MinimumStock"])
            if self.QtblXuatThongTin_3.item(7, 0) is None:
                self.QtblXuatThongTin_3.setItem(7, 0, QTableWidgetItem(value))
            else:
                self.QtblXuatThongTin_3.item(7, 0).setText(value)

        # Clear quantity field for new input
        if self.QtblXuatThongTin_3.item(4, 0) is None:
            self.QtblXuatThongTin_3.setItem(4, 0, QTableWidgetItem(""))
        else:
            self.QtblXuatThongTin_3.item(4, 0).setText("")

        # Set import date to current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        if self.QtblXuatThongTin_3.item(5, 0) is None:
            self.QtblXuatThongTin_3.setItem(5, 0, QTableWidgetItem(current_date))
        else:
            self.QtblXuatThongTin_3.item(5, 0).setText(current_date)

        # Clear expiration date for new input
        if self.QtblXuatThongTin_3.item(6, 0) is None:
            self.QtblXuatThongTin_3.setItem(6, 0, QTableWidgetItem(""))
        else:
            self.QtblXuatThongTin_3.item(6, 0).setText("")

    def display_product_info(self, product_data):
        """Display product info in the QtblXuatThongTin_4 table"""
        # Map MongoDB fields to table rows
        field_mapping = {
            "ProductID": 0,
            "Name": 1,
            "Category": 2,
            "UnitPrice": 3,
            "Quantity": 4,
            "Status": 5,
            "ImportDate": 6,
            "ExpirationDate": 7,
            "MinimumStock": 8
        }

        # Fill in the product information table
        for field, row in field_mapping.items():
            if field in product_data:
                value = str(product_data[field])
                if self.QtblXuatThongTin_4.item(row, 0) is None:
                    self.QtblXuatThongTin_4.setItem(row, 0, QTableWidgetItem(value))
                else:
                    self.QtblXuatThongTin_4.item(row, 0).setText(value)

    def xoa_du_lieu_nhap(self):
        """Clear all input fields in the input table"""
        for row in range(self.QtblXuatThongTin_3.rowCount()):
            if self.QtblXuatThongTin_3.item(row, 0) is None:
                self.QtblXuatThongTin_3.setItem(row, 0, QTableWidgetItem(""))
            else:
                self.QtblXuatThongTin_3.item(row, 0).setText("")

        # Clear the product info table as well
        for row in range(self.QtblXuatThongTin_4.rowCount()):
            if self.QtblXuatThongTin_4.item(row, 0) is None:
                self.QtblXuatThongTin_4.setItem(row, 0, QTableWidgetItem(""))
            else:
                self.QtblXuatThongTin_4.item(row, 0).setText("")

        # Reset import date to current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.QtblXuatThongTin_3.item(5, 0).setText(current_date)

    def nhap_kho(self):
        """Handle warehouse input action"""
        # Confirm with user
        confirm_box = QMessageBox()
        confirm_box.setIcon(QMessageBox.Icon.Question)
        confirm_box.setWindowTitle("Xác nhận nhập kho")
        confirm_box.setText("Bạn có muốn nhập kho không?")
        confirm_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        result = confirm_box.exec()

        if result == QMessageBox.StandardButton.Yes:
            self.process_warehouse_input()

    def get_table_value(self, table, row, col):
        """Safely get a value from a table cell"""
        item = table.item(row, col)
        if item is None:
            return ""
        return item.text().strip()

    def update_product_status(self, product_id, quantity, min_stock):
        """Update product status based on quantity"""
        status = "Còn hàng" if quantity > min_stock else "Sắp hết hàng" if quantity > 0 else "Hết hàng"

        collection.update_one(
            {"ProductID": product_id},
            {"$set": {"Status": status}}
        )

    def process_warehouse_input(self):
        """Thu thập dữ liệu từ các ô nhập và lưu (hoặc cập nhật) vào MongoDB"""
        try:
            product_data = {
                "ProductID": self.get_table_value(self.QtblXuatThongTin_3, 0, 0),
                "Name": self.get_table_value(self.QtblXuatThongTin_3, 1, 0),
                "Category": self.get_table_value(self.QtblXuatThongTin_3, 2, 0),
                "UnitPrice": int(self.get_table_value(self.QtblXuatThongTin_3, 3, 0)),
                "Quantity": int(self.get_table_value(self.QtblXuatThongTin_3, 4, 0)),
                "ImportDate": self.get_table_value(self.QtblXuatThongTin_3, 5, 0),
                "ExpirationDate": self.get_table_value(self.QtblXuatThongTin_3, 6, 0),
                "MinimumStock": int(self.get_table_value(self.QtblXuatThongTin_3, 7, 0)),
                "Status": self.get_table_value(self.QtblXuatThongTin_3, 8, 0)
            }

            # Kiểm tra các trường bắt buộc
            required_fields = ["ProductID", "Name", "Category", "UnitPrice", "Quantity"]
            for field in required_fields:
                if not product_data[field]:
                    QMessageBox.warning(self.MainWindow, "Lỗi nhập liệu",
                                        f"Vui lòng nhập đầy đủ thông tin {field}")
                    return

            # Kiểm tra xem sản phẩm đã tồn tại trong MongoDB hay chưa
            existing_product = collection.find_one({"ProductID": product_data["ProductID"]})
            if existing_product:
                # Nếu sản phẩm đã tồn tại: cập nhật số lượng và các thông tin khác
                new_quantity = existing_product["Quantity"] + product_data["Quantity"]
                update_data = {
                    "Quantity": new_quantity,
                    "ImportDate": product_data["ImportDate"],
                    "ExpirationDate": product_data["ExpirationDate"]
                }
                collection.update_one(
                    {"ProductID": product_data["ProductID"]},
                    {"$set": update_data}
                )
                # Cập nhật trạng thái sản phẩm dựa trên số lượng mới
                self.update_product_status(product_data["ProductID"], new_quantity,
                                           int(existing_product["MinimumStock"]))
                QMessageBox.information(self.MainWindow, "Thành công",
                                        f"Đã cập nhật số lượng sản phẩm {product_data['Name']}")
            else:
                # Nếu sản phẩm chưa có: thêm sản phẩm mới vào MongoDB
                collection.insert_one(product_data)
                QMessageBox.information(self.MainWindow, "Thành công",
                                        f"Đã thêm sản phẩm mới: {product_data['Name']}")

            # Xóa dữ liệu nhập sau khi lưu thành công
            self.xoa_du_lieu_nhap()

        except ValueError as e:
            QMessageBox.warning(self.MainWindow, "Lỗi nhập liệu", "bạn cần nhập đúng định dạnh, không được bỏ trống")
        except Exception as e:
            QMessageBox.critical(self.MainWindow, "Lỗi",
                                 f"Đã xảy ra lỗi: {str(e)}")