from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QMessageBox, QProgressBar, QDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject

# Import hardware modules
try:
    from hardware.device import HighGaugeDevice
except ImportError:
    try:
        from src.hardware.device import HighGaugeDevice
    except ImportError:
        from ..hardware.device import HighGaugeDevice

# Import model modules
try:
    from models.model_manager import ModelManager
    from models.parameter_manager import ParameterManager
    from models.measurement_manager import MeasurementManager
except ImportError:
    try:
        from src.models.model_manager import ModelManager
        from src.models.parameter_manager import ParameterManager
        from src.models.measurement_manager import MeasurementManager
    except ImportError:
        from ..models.model_manager import ModelManager
        from ..models.parameter_manager import ParameterManager
        from ..models.measurement_manager import MeasurementManager

# Import config modules
try:
    from config.database import DatabaseConfig
except ImportError:
    try:
        from src.config.database import DatabaseConfig
    except ImportError:
        from ..config.database import DatabaseConfig

class DeviceConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kết nối thiết bị")
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background: #f8fafc;
            }
            QLabel {
                color: #1e293b;
                font-size: 14px;
            }
            QPushButton {
                background: #e53935;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #b71c1c;
            }
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 16px;
                background: white;
            }
            QComboBox:hover {
                border-color: #e53935;
            }
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
                background: white;
                font-family: monospace;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Combo box chọn cổng COM
        self.port_combo = QComboBox()
        self.refresh_ports()
        
        # Nút làm mới danh sách cổng
        refresh_btn = QPushButton("Làm mới")
        refresh_btn.clicked.connect(self.refresh_ports)
        
        # Nút kết nối
        connect_btn = QPushButton("Kết nối")
        connect_btn.clicked.connect(self.connect_device)
        
        # Text area hiển thị thông tin thiết bị
        self.device_info = QTextEdit()
        self.device_info.setReadOnly(True)
        self.device_info.setMinimumHeight(150)
        
        layout.addWidget(QLabel("Chọn cổng COM:"))
        layout.addWidget(self.port_combo)
        layout.addWidget(refresh_btn)
        layout.addWidget(QLabel("Thông tin thiết bị:"))
        layout.addWidget(self.device_info)
        layout.addWidget(connect_btn)
        
    def refresh_ports(self):
        """Làm mới danh sách cổng COM"""
        self.port_combo.clear()
        ports = HighGaugeDevice.list_ports()
        self.port_combo.addItems(ports)
        
    def get_selected_port(self):
        """Lấy cổng COM được chọn"""
        return self.port_combo.currentText()
        
    def connect_device(self):
        """Kết nối với thiết bị và hiển thị thông tin"""
        port = self.get_selected_port()
        if not port:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn cổng COM!")
            return
            
        try:
            # Tạo kết nối tạm thời để đọc thông tin
            temp_device = HighGaugeDevice()
            if temp_device.connect(port):
                # Đọc thông tin thiết bị
                device_info = temp_device.get_device_info()
                if device_info:
                    self.device_info.setText(device_info)
                    # Chấp nhận kết nối
                    self.accept()
                else:
                    QMessageBox.warning(self, "Cảnh báo", "Không thể đọc thông tin thiết bị!")
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể kết nối với thiết bị!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi kết nối thiết bị: {str(e)}")
        finally:
            if 'temp_device' in locals():
                temp_device.disconnect()

class ModelLoaderWorker(QObject):
    finished = pyqtSignal(list)
    def run(self):
        try:
            models = ModelManager().get_all_models()
            self.finished.emit(models)
        except Exception as e:
            print(f"Lỗi khi load_models (QThread): {e}")
            self.finished.emit([])

class MeasurementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("Đã vào MeasurementWidget.__init__()")
        self.device = HighGaugeDevice()
        self.model_manager = ModelManager()
        self.parameter_manager = ParameterManager()
        self.measurement_manager = MeasurementManager()
        self.db_config = DatabaseConfig()
        self.current_model_id = None
        self.current_parameter_id = None
        self.current_value = None
        self.measurement_timer = QTimer()
        self.measurement_timer.timeout.connect(self.read_device_data)
        self.setStyleSheet("""
            QWidget {
                background: #f8fafc;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #1e293b;
                font-size: 14px;
            }
            QPushButton {
                background: #e53935;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #b71c1c;
            }
            QPushButton:disabled {
                background: #94a3b8;
            }
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 16px;
                background: white;
            }
            QComboBox:hover {
                border-color: #e53935;
            }
            QProgressBar {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                text-align: center;
                background: white;
            }
            QProgressBar::chunk {
                background: #e53935;
                border-radius: 8px;
            }
        """)
        print("Trước khi init_ui trong MeasurementWidget")
        self.init_ui()
        print("Trước khi load_models bằng QThread trong MeasurementWidget")
        self.load_models_qthread()
        print("Sau khi load_models_qthread trong MeasurementWidget")
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Phần chọn model
        model_layout = QHBoxLayout()
        model_label = QLabel("Chọn Model:")
        self.model_combo = QComboBox()
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)
        
        # Phần chọn thông số
        parameter_layout = QHBoxLayout()
        parameter_label = QLabel("Thông số:")
        self.parameter_combo = QComboBox()
        parameter_layout.addWidget(parameter_label)
        parameter_layout.addWidget(self.parameter_combo)
        layout.addLayout(parameter_layout)
        
        # Phần kết nối thiết bị
        device_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Kết nối thiết bị")
        self.connect_btn.clicked.connect(self.connect_device)
        device_layout.addWidget(self.connect_btn)
        layout.addLayout(device_layout)
        
        # Phần hiển thị giá trị đo
        value_layout = QVBoxLayout()
        self.value_label = QLabel("Giá trị: --")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("font-size: 24pt;")
        value_layout.addWidget(self.value_label)
        
        # Thanh tiến trình
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        value_layout.addWidget(self.progress_bar)
        
        layout.addLayout(value_layout)
        
        # Phần nút điều khiển
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("Bắt đầu đo")
        self.start_btn.clicked.connect(self.start_measurement)
        self.start_btn.setEnabled(False)
        
        self.save_btn = QPushButton("Lưu kết quả")
        self.save_btn.clicked.connect(self.save_measurement)
        self.save_btn.setEnabled(False)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.save_btn)
        layout.addLayout(control_layout)

    def load_models_qthread(self):
        try:
            print("Bắt đầu tạo QThread...")
            self.thread = QThread()
            self.worker = ModelLoaderWorker()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.update_models_ui)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            print("Bắt đầu QThread...")
            self.thread.start()
        except Exception as e:
            print(f"Lỗi khi tạo QThread: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách model: {str(e)}")

    def update_models_ui(self, models):
        try:
            print(f"Cập nhật UI với {len(models)} models")
            self.model_combo.clear()
            for model in models:
                self.model_combo.addItem(model['name'], model['id'])
            print("Đã cập nhật UI thành công")
        except Exception as e:
            print(f"Lỗi khi cập nhật UI: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật giao diện: {str(e)}")

    def load_parameters(self, model_id):
        try:
            parameters = self.parameter_manager.get_parameters_by_model(model_id)
            self.parameter_combo.clear()
            for param in parameters:
                self.parameter_combo.addItem(param['name'], param['id'])
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách thông số: {str(e)}")

    def connect_device(self):
        try:
            dialog = DeviceConnectionDialog(self)
            if dialog.exec():
                port = dialog.get_selected_port()
                if self.device.connect(port):
                    self.connect_btn.setEnabled(False)
                    self.start_btn.setEnabled(True)
                    QMessageBox.information(self, "Thành công", "Đã kết nối thiết bị thành công!")
                else:
                    QMessageBox.critical(self, "Lỗi", "Không thể kết nối thiết bị!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi kết nối thiết bị: {str(e)}")

    def start_measurement(self):
        try:
            self.measurement_timer.start(1000)  # Đọc dữ liệu mỗi giây
            self.start_btn.setText("Dừng đo")
            self.start_btn.clicked.disconnect()
            self.start_btn.clicked.connect(self.stop_measurement)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể bắt đầu đo: {str(e)}")

    def stop_measurement(self):
        try:
            self.measurement_timer.stop()
            self.start_btn.setText("Bắt đầu đo")
            self.start_btn.clicked.disconnect()
            self.start_btn.clicked.connect(self.start_measurement)
            self.save_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể dừng đo: {str(e)}")

    def read_device_data(self):
        try:
            value = self.device.read()
            if value is not None:
                self.current_value = value
                self.value_label.setText(f"Giá trị: {value:.3f}")
                self.progress_bar.setValue(int(value * 100))
        except Exception as e:
            print(f"Lỗi đọc dữ liệu: {e}")
            self.stop_measurement()
            QMessageBox.critical(self, "Lỗi", f"Không thể đọc dữ liệu từ thiết bị: {str(e)}")

    def save_measurement(self):
        try:
            if self.current_value is None:
                QMessageBox.warning(self, "Cảnh báo", "Chưa có giá trị đo để lưu!")
                return
                
            if self.current_model_id is None or self.current_parameter_id is None:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn model và thông số!")
                return
                
            self.measurement_manager.add_measurement(
                self.current_parameter_id,
                self.current_value
            )
            QMessageBox.information(self, "Thành công", "Đã lưu kết quả đo!")
            self.save_btn.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu kết quả đo: {str(e)}")

    def set_model(self, model_id):
        try:
            self.current_model_id = model_id
            self.load_parameters(model_id)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thiết lập model: {str(e)}") 