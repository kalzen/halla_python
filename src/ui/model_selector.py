from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal, Qt, QThread, QObject, QTimer

# Import model modules
try:
    from models.model_manager import ModelManager
except ImportError:
    try:
        from src.models.model_manager import ModelManager
    except ImportError:
        from ..models.model_manager import ModelManager

# Import UI modules
try:
    from ui.model_management import AddModelDialog
except ImportError:
    try:
        from src.ui.model_management import AddModelDialog
    except ImportError:
        from .model_management import AddModelDialog

class ModelLoaderWorker(QObject):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def run(self):
        try:
            model_manager = ModelManager()
            models = model_manager.get_all_models()
            print(f"Số lượng model lấy được (QThread): {len(models)}")
            self.finished.emit(models)
        except Exception as e:
            print(f"Lỗi khi load_models (QThread): {e}")
            self.error.emit(str(e))
            self.finished.emit([])

class ModelSelectorWidget(QWidget):
    model_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            print("Đã vào ModelSelectorWidget.__init__()")
            self.setStyleSheet('''
                QWidget { 
                    background: #f8fafc; 
                    font-family: 'Segoe UI', sans-serif;
                }
                QLabel { 
                    font-size: 28px; 
                    font-weight: bold; 
                    color: #222; 
                    margin-bottom: 24px; 
                }
                QComboBox, QPushButton {
                    font-size: 22px; 
                    padding: 12px 24px; 
                    border-radius: 12px;
                    border: 1px solid #d1d5db; 
                    background: #fff; 
                    margin-bottom: 18px;
                }
                QPushButton {
                    background: #e53935; 
                    color: #fff; 
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover { 
                    background: #b71c1c; 
                }
            ''')
            print("Đã set stylesheet")
            
            layout = QVBoxLayout()
            self.setLayout(layout)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            print("Đang tạo các widget con...")
            self.label = QLabel("Chọn Model để bắt đầu")
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.combo = QComboBox()
            self.btn_add = QPushButton("Thêm model mới")
            self.btn_add.clicked.connect(self.add_model_dialog)
            self.btn_start = QPushButton("Bắt đầu đo")
            self.btn_start.clicked.connect(self.emit_selected)
            
            print("Đang thêm widget vào layout...")
            layout.addWidget(self.label)
            layout.addWidget(self.combo)
            layout.addWidget(self.btn_start)
            layout.addWidget(self.btn_add)
            
            print("Trước khi load_models bằng QThread trong ModelSelectorWidget")
            self.load_models_qthread()
            print("Đã khởi tạo ModelSelectorWidget thành công")
        except Exception as e:
            print(f"Lỗi khởi tạo ModelSelectorWidget: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể khởi tạo giao diện: {str(e)}")

    def load_models_qthread(self):
        try:
            print("Bắt đầu tạo QThread...")
            self.thread = QThread()
            self.worker = ModelLoaderWorker()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.update_models_ui)
            self.worker.error.connect(self.handle_error)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            print("Bắt đầu QThread...")
            self.thread.start()
        except Exception as e:
            print(f"Lỗi khi tạo QThread: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách model: {str(e)}")

    def handle_error(self, error_msg):
        print(f"Lỗi từ worker: {error_msg}")
        QMessageBox.warning(self, "Cảnh báo", 
            f"Không thể tải danh sách model: {error_msg}\n"
            "Một số tính năng có thể không hoạt động.")

    def update_models_ui(self, models):
        try:
            print(f"Cập nhật UI với {len(models)} models")
            self.combo.clear()
            if not models or len(models) == 0:
                self.label.setText("Chưa có model nào. Vui lòng thêm model mới!")
                self.combo.setEnabled(False)
                self.btn_start.setEnabled(False)
                self.btn_add.setVisible(True)
                print("Không có model nào, chỉ hiển thị nút thêm model mới.")
                return
            self.label.setText("Chọn Model để bắt đầu")
            for m in models:
                self.combo.addItem(m['name'], m['id'])
            self.combo.setEnabled(True)
            self.btn_start.setEnabled(True)
            self.btn_add.setVisible(True)
            print("Đã cập nhật UI thành công")
        except Exception as e:
            print(f"Lỗi khi cập nhật UI: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật giao diện: {str(e)}")

    def add_model_dialog(self):
        try:
            dlg = AddModelDialog(self)
            if dlg.exec():
                QTimer.singleShot(0, self.load_models_qthread)
        except Exception as e:
            print(f"Lỗi khi mở dialog thêm model: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể mở form thêm model: {str(e)}")

    def emit_selected(self):
        try:
            model_id = self.combo.currentData()
            if model_id:
                self.model_selected.emit(model_id)
        except Exception as e:
            print(f"Lỗi khi chọn model: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể chọn model: {str(e)}") 