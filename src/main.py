import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QMessageBox, QHBoxLayout
from PyQt6.QtCore import Qt

# Import database config
try:
    from config.database import DatabaseConfig
except ImportError:
    try:
        from src.config.database import DatabaseConfig
    except ImportError:
        from .config.database import DatabaseConfig

# Import UI modules
try:
    from ui.measurement import MeasurementWidget
    from ui.dashboard import DashboardWidget
    from ui.template_management import TemplateManagementWidget
    from ui.model_management import ModelManagementWidget
    from ui.report_generator import ReportGeneratorWidget
    from ui.backup_management import BackupManagementWidget
    from ui.model_selector import ModelSelectorWidget
except ImportError:
    try:
        from src.ui.measurement import MeasurementWidget
        from src.ui.dashboard import DashboardWidget
        from src.ui.template_management import TemplateManagementWidget
        from src.ui.model_management import ModelManagementWidget
        from src.ui.report_generator import ReportGeneratorWidget
        from src.ui.backup_management import BackupManagementWidget
        from src.ui.model_selector import ModelSelectorWidget
    except ImportError:
        from .ui.measurement import MeasurementWidget
        from .ui.dashboard import DashboardWidget
        from .ui.template_management import TemplateManagementWidget
        from .ui.model_management import ModelManagementWidget
        from .ui.report_generator import ReportGeneratorWidget
        from .ui.backup_management import BackupManagementWidget
        from .ui.model_selector import ModelSelectorWidget

def main():
    try:
        print("Bắt đầu tạo QApplication")
        app = QApplication(sys.argv)
        
        print("Tạo MainWindow")
        window = MainWindow()
        
        print("Show MainWindow")
        window.show()
        
        print("Bắt đầu app.exec()")
        return app.exec()
    except Exception as e:
        print(f"Lỗi trong main: {str(e)}")
        print(traceback.format_exc())
        QMessageBox.critical(None, "Lỗi", f"Không thể khởi động ứng dụng: {str(e)}")
        return 1

class MainWindow(QMainWindow):
    def __init__(self):
        try:
            print("Bắt đầu khởi tạo MainWindow")
            super().__init__()
            self.setWindowTitle("Halla Measurement System")
            self.setMinimumSize(1280, 800)
            print("Đã thiết lập kích thước cửa sổ")

            # Tạo central widget
            print("Bắt đầu tạo central widget")
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            print("Đã tạo central widget")

            # Kiểm tra kết nối database
            try:
                print("Bắt đầu kiểm tra kết nối database...")
                db_config = DatabaseConfig()
                conn = db_config.get_connection()
                if conn:
                    print("Đã kết nối thành công đến database")
                    conn.close()
                else:
                    print("Không thể kết nối đến database")
                    QMessageBox.warning(self, "Cảnh báo", 
                        "Không thể kết nối đến database. Một số tính năng có thể không hoạt động.\n"
                        "Vui lòng kiểm tra:\n"
                        "1. MySQL đã được cài đặt và đang chạy\n"
                        "2. Database 'halla' đã được tạo\n"
                        "3. Thông tin kết nối trong file .env là chính xác")
            except Exception as e:
                print(f"Lỗi kết nối database: {str(e)}")
                print(traceback.format_exc())
                QMessageBox.warning(self, "Cảnh báo", 
                    f"Không thể kết nối đến database: {str(e)}\n"
                    "Một số tính năng có thể không hoạt động.")

            print("Bắt đầu khởi tạo UI")
            self.init_ui()
            print("Đã khởi tạo UI xong")

            print("Bắt đầu hiển thị cửa sổ")
            self.show()
            print("Đã hiển thị cửa sổ xong")

        except Exception as e:
            print(f"Lỗi khởi tạo MainWindow: {str(e)}")
            print(traceback.format_exc())
            QMessageBox.critical(self, "Lỗi", f"Không thể khởi tạo ứng dụng: {str(e)}")
            sys.exit(1)

    def init_ui(self):
        try:
            print("Bắt đầu khởi tạo UI")
            layout = QVBoxLayout(self.central_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            print("Đã thiết lập layout")

            # Header
            print("Bắt đầu tạo header")
            header = QWidget()
            header.setStyleSheet("""
                QWidget {
                    background: #b71c1c;
                    padding: 16px;
                }
                QLabel {
                    color: white;
                    font-size: 24px;
                    font-weight: 600;
                }
            """)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(24, 16, 24, 16)
            
            title = QLabel("Halla Measurement System")
            header_layout.addWidget(title)
            print("Đã tạo header")
            
            layout.addWidget(header)
            print("Đã thêm header vào layout")

            # Main content
            print("Bắt đầu tạo content")
            content = QWidget()
            content_layout = QHBoxLayout(content)
            content_layout.setContentsMargins(24, 24, 24, 24)
            content_layout.setSpacing(24)
            print("Đã tạo content layout")

            # Left sidebar
            print("Bắt đầu tạo sidebar")
            sidebar = QWidget()
            sidebar.setFixedWidth(200)
            sidebar.setStyleSheet("""
                QWidget {
                    background: white;
                    border-radius: 12px;
                }
                QPushButton {
                    text-align: left;
                    padding: 12px 16px;
                    border: none;
                    border-radius: 8px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #fecaca;
                }
                QPushButton:checked {
                    background: #e53935;
                    color: white;
                }
            """)
            sidebar_layout = QVBoxLayout(sidebar)
            sidebar_layout.setContentsMargins(16, 16, 16, 16)
            sidebar_layout.setSpacing(8)
            print("Đã tạo sidebar")

            # Navigation buttons
            print("Bắt đầu tạo navigation buttons")
            self.nav_buttons = []
            nav_items = [
                ("Dashboard", "dashboard"),
                ("Quản lý Model", "model_management"),
                ("Đo lường", "measurement"),
                ("Báo cáo", "report"),
                ("Sao lưu", "backup"),
                ("Quản lý Template", "template")
            ]
            
            for text, name in nav_items:
                btn = QPushButton(text)
                btn.setCheckable(True)
                btn.setProperty("page", name)
                btn.clicked.connect(self.on_nav_click)
                sidebar_layout.addWidget(btn)
                self.nav_buttons.append(btn)
            print("Đã tạo các nút navigation")

            # Add spacer to push buttons to the top
            sidebar_layout.addStretch()
            content_layout.addWidget(sidebar)
            print("Đã thêm sidebar vào content layout")

            # Right content area
            print("Bắt đầu tạo content stack")
            self.content_stack = QStackedWidget()
            self.content_stack.setStyleSheet("""
                QStackedWidget {
                    background: transparent;
                }
            """)
            print("Đã tạo content stack")

            # Initialize pages
            print("Bắt đầu khởi tạo các trang")
            try:
                self.pages = {
                    "dashboard": DashboardWidget(),
                    "model_management": ModelManagementWidget(),
                    "measurement": MeasurementWidget(),
                    "report": ReportGeneratorWidget(),
                    "backup": BackupManagementWidget(),
                    "template": TemplateManagementWidget()
                }
                print("Đã khởi tạo các trang")

                for page in self.pages.values():
                    self.content_stack.addWidget(page)
                print("Đã thêm các trang vào content stack")
            except Exception as e:
                print(f"Lỗi khởi tạo các trang: {str(e)}")
                print(traceback.format_exc())
                raise

            content_layout.addWidget(self.content_stack)
            layout.addWidget(content)
            print("Đã thêm content vào layout chính")

            # Set initial page
            self.nav_buttons[0].setChecked(True)
            self.content_stack.setCurrentWidget(self.pages["dashboard"])
            print("Đã thiết lập trang mặc định")

        except Exception as e:
            print(f"Lỗi trong init_ui: {str(e)}")
            print(traceback.format_exc())
            raise

    def on_nav_click(self):
        try:
            print("Bắt đầu xử lý sự kiện click navigation")
            clicked_button = self.sender()
            page_name = clicked_button.property("page")
            print(f"Đã click vào nút {page_name}")

            # Uncheck all buttons
            for btn in self.nav_buttons:
                btn.setChecked(False)
            print("Đã bỏ chọn tất cả các nút")

            # Check clicked button
            clicked_button.setChecked(True)
            print(f"Đã chọn nút {page_name}")

            # Show corresponding page
            self.content_stack.setCurrentWidget(self.pages[page_name])
            print(f"Đã chuyển đến trang {page_name}")
        except Exception as e:
            print(f"Lỗi trong on_nav_click: {str(e)}")
            print(traceback.format_exc())

if __name__ == "__main__":
    try:
        print("Bắt đầu chạy ứng dụng")
        app = QApplication(sys.argv)
        print("Đã tạo QApplication")
        window = MainWindow()
        print("Đã tạo MainWindow")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Lỗi trong main: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1) 