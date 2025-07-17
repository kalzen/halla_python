from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QComboBox, QTableWidget, QTableWidgetItem, QGroupBox, 
                            QGridLayout, QSizePolicy, QFrame, QDialog, QLineEdit, QTextEdit, QListWidget)
from PyQt6.QtGui import QPixmap, QColor, QPalette, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QRect, pyqtProperty, pyqtSignal, QTimer
import matplotlib
matplotlib.use('Qt5Agg')  # Sử dụng Qt5Agg backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import plotly.io as pio

# Import serial với error handling
try:
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    print("Warning: pyserial not available - device connection disabled")
    SERIAL_AVAILABLE = False

# Import model modules
try:
    from models.dashboard_manager import DashboardManager
    from models.model_manager import ModelManager
    from models.measurement_manager import MeasurementManager
except ImportError:
    try:
        from src.models.dashboard_manager import DashboardManager
        from src.models.model_manager import ModelManager
        from src.models.measurement_manager import MeasurementManager
    except ImportError:
        from ..models.dashboard_manager import DashboardManager
        from ..models.model_manager import ModelManager
        from ..models.measurement_manager import MeasurementManager

# Import UI modules
try:
    from .plot_widget import PlotWidget
    from .model_selector_dialog import ModelSelectorDialog
    from .measurement import MeasurementWidget
except ImportError:
    try:
        from src.ui.plot_widget import PlotWidget
        from src.ui.model_selector_dialog import ModelSelectorDialog
        from src.ui.measurement import MeasurementWidget
    except ImportError:
        from plot_widget import PlotWidget
        from model_selector_dialog import ModelSelectorDialog
        from measurement import MeasurementWidget

# Import hardware modules
try:
    from hardware.device import HighGaugeDevice
except ImportError:
    try:
        from src.hardware.device import HighGaugeDevice
    except ImportError:
        from ..hardware.device import HighGaugeDevice

class MeasurementDialog(QDialog):
    def __init__(self, model_id, parent=None):
        print(f"Debug: MeasurementDialog.__init__ called with model_id = {model_id}")
        super().__init__(parent)
        self.model_id = model_id
        self.device = None
        
        try:
            print("Debug: Creating measurement manager...")
            self.measurement_manager = MeasurementManager()
            print("Debug: Creating model manager...")
            self.model_manager = ModelManager()
            self.current_values = {}
            self.measurement_timer = QTimer()
            self.measurement_timer.timeout.connect(self.read_measurement)
            self.parameters_list = []  # Danh sách các thông số theo thứ tự
            self.current_param_index = 0  # Index của thông số hiện tại
            
            self.setWindowTitle("Đo lường sản phẩm")
            self.setModal(True)
            self.setMinimumSize(600, 500)
            print("Debug: Basic setup completed")
        except Exception as e:
            print(f"Debug: Error in MeasurementDialog init: {e}")
            raise
        self.setStyleSheet("""
            QDialog {
                background: #f8fafc;
            }
            QLabel {
                color: #1e293b;
                font-size: 14px;
                background: transparent;
            }
            QLabel#title {
                font-size: 18px;
                font-weight: 600;
                color: #e53935;
                background: transparent;
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
            QComboBox, QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 16px;
                background: white;
            }
            QComboBox:hover, QLineEdit:hover {
                border-color: #e53935;
            }
            QListWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
                font-family: monospace;
            }
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
                font-family: monospace;
            }
        """)
        
        try:
            print("Debug: Calling init_ui...")
            self.init_ui()
            print("Debug: Calling load_model_info...")
            self.load_model_info()
            print("Debug: Calling scan_devices...")
            self.scan_devices()
            print("Debug: MeasurementDialog initialization completed")
        except Exception as e:
            print(f"Debug: Error during dialog initialization: {e}")
            import traceback
            traceback.print_exc()
            raise

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Đo lường sản phẩm")
        header.setObjectName("title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Model info
        self.model_info_label = QLabel()
        layout.addWidget(self.model_info_label)
        
        # Device selection
        device_group = QGroupBox("Kết nối thiết bị")
        device_layout = QVBoxLayout(device_group)
        
        # Device list
        device_header = QHBoxLayout()
        device_header.addWidget(QLabel("Thiết bị có sẵn:"))
        refresh_btn = QPushButton("Làm mới")
        refresh_btn.clicked.connect(self.scan_devices)
        device_header.addWidget(refresh_btn)
        device_layout.addLayout(device_header)
        
        self.device_list = QListWidget()
        self.device_list.setMaximumHeight(100)
        device_layout.addWidget(self.device_list)
        
        # Connect button
        connect_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Kết nối thiết bị")
        self.connect_btn.clicked.connect(self.connect_device)
        connect_layout.addWidget(self.connect_btn)
        
        self.manual_btn = QPushButton("Nhập thủ công")
        self.manual_btn.clicked.connect(self.toggle_manual_mode)
        connect_layout.addWidget(self.manual_btn)
        connect_layout.addStretch()
        device_layout.addLayout(connect_layout)
        
        layout.addWidget(device_group)
        
        # Measurement section
        measure_group = QGroupBox("Đo lường")
        measure_layout = QVBoxLayout(measure_group)
        
        # Parameters
        self.param_layout = QVBoxLayout()
        measure_layout.addLayout(self.param_layout)
        
        # Manual input area (hidden by default)
        self.manual_widget = QWidget()
        self.manual_widget.setVisible(False)
        manual_layout = QVBoxLayout(self.manual_widget)
        manual_layout.addWidget(QLabel("Nhập giá trị thủ công:"))
        self.manual_inputs = {}
        measure_layout.addWidget(self.manual_widget)
        
        # Status
        self.status_label = QLabel("Chưa kết nối thiết bị")
        measure_layout.addWidget(self.status_label)
        
        # Control buttons
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("Bắt đầu đo")
        self.start_btn.clicked.connect(self.start_measurement)
        self.start_btn.setEnabled(False)
        control_layout.addWidget(self.start_btn)
        
        self.save_btn = QPushButton("Lưu kết quả")
        self.save_btn.clicked.connect(self.save_measurement)
        self.save_btn.setEnabled(False)
        control_layout.addWidget(self.save_btn)
        
        control_layout.addStretch()
        
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.close)
        control_layout.addWidget(close_btn)
        
        measure_layout.addLayout(control_layout)
        layout.addWidget(measure_group)

    def load_model_info(self):
        """Load thông tin model"""
        try:
            print(f"Debug: Loading model info for model_id = {self.model_id}")
            model = self.model_manager.get_model_by_id(self.model_id)
            if model:
                print(f"Debug: Model found: {model['name']}")
                self.model_info_label.setText(f"Model: {model['name']}")
                # Load parameters
                print("Debug: Loading parameters...")
                parameters = self.model_manager.get_parameters_by_model(self.model_id)
                print(f"Debug: Found {len(parameters)} parameters")
                self.load_parameters(parameters)
            else:
                print("Debug: Model not found")
                self.model_info_label.setText(f"Model ID {self.model_id} không tìm thấy")
                # Tạo parameters giả để test
                self.load_parameters([
                    {'id': 1, 'name': 'Thông số 1', 'unit': 'mm'},
                    {'id': 2, 'name': 'Thông số 2', 'unit': 'kg'}
                ])
        except Exception as e:
            print(f"Debug: Error loading model info: {e}")
            import traceback
            traceback.print_exc()
            self.model_info_label.setText(f"Lỗi load model: {str(e)}")
            # Tạo parameters giả để test
            self.load_parameters([
                {'id': 1, 'name': 'Test Param', 'unit': 'unit'}
            ])

    def load_parameters(self, parameters):
        """Load các thông số cần đo"""
        # Lưu danh sách parameters
        self.parameters_list = parameters
        self.current_param_index = 0
        
        # Clear existing widgets
        for i in reversed(range(self.param_layout.count())):
            self.param_layout.itemAt(i).widget().setParent(None)
        
        self.param_labels = {}
        self.manual_inputs.clear()
        
        for i, param in enumerate(parameters):
            param_widget = QWidget()
            param_layout = QHBoxLayout(param_widget)
            
            # Indicator cho thông số hiện tại
            indicator = QLabel("👉" if i == 0 else "  ")
            indicator.setMinimumWidth(30)
            param_layout.addWidget(indicator)
            
            # Parameter name and current value
            name_label = QLabel(f"{param['name']}:")
            name_label.setMinimumWidth(100)
            param_layout.addWidget(name_label)
            
            value_label = QLabel("--")
            value_label.setStyleSheet("font-weight: bold; color: #e53935;")
            param_layout.addWidget(value_label)
            
            unit_label = QLabel(param.get('unit', ''))
            param_layout.addWidget(unit_label)
            
            param_layout.addStretch()
            
            self.param_labels[param['id']] = value_label
            # Lưu cả indicator để có thể update sau
            setattr(self, f"param_indicator_{param['id']}", indicator)
            self.param_layout.addWidget(param_widget)
            
            # Manual input (hidden by default)
            manual_input = QLineEdit()
            manual_input.setPlaceholderText(f"Nhập {param['name']}")
            manual_input.setVisible(False)
            # Enable Enter key để chuyển thông số tiếp
            manual_input.returnPressed.connect(lambda: self.save_current_parameter())
            self.manual_inputs[param['id']] = manual_input
            self.param_layout.addWidget(manual_input)
            
        # Update status để hiển thị thông số hiện tại
        if parameters:
            self.update_current_parameter_display()

    def update_current_parameter_display(self):
        """Cập nhật hiển thị thông số hiện tại"""
        if not self.parameters_list:
            return
            
        # Reset tất cả indicators
        for i, param in enumerate(self.parameters_list):
            indicator = getattr(self, f"param_indicator_{param['id']}", None)
            if indicator:
                indicator.setText("👉" if i == self.current_param_index else "  ")
                
        # Highlight thông số hiện tại
        current_param = self.parameters_list[self.current_param_index]
        self.status_label.setText(f"📝 Đang đo: {current_param['name']} ({current_param.get('unit', '')})")
        
        # Focus vào input của thông số hiện tại nếu đang ở manual mode
        if self.manual_widget.isVisible() and current_param['id'] in self.manual_inputs:
            self.manual_inputs[current_param['id']].setFocus()
    
    def save_current_parameter(self):
        """Lưu thông số hiện tại và chuyển sang thông số tiếp theo"""
        if not self.parameters_list or self.current_param_index >= len(self.parameters_list):
            return
            
        current_param = self.parameters_list[self.current_param_index]
        param_id = current_param['id']
        
        # Đọc giá trị từ input
        if param_id in self.manual_inputs:
            input_widget = self.manual_inputs[param_id]
            value_text = input_widget.text().strip()
            
            if value_text:
                try:
                    value = float(value_text)
                    
                    # Lưu vào database ngay lập tức
                    measurement_id = self.measurement_manager.add_measurement(
                        model_id=self.model_id,
                        parameter_id=param_id,
                        value=value
                    )
                    
                    if measurement_id:
                        # Cập nhật hiển thị
                        self.param_labels[param_id].setText(f"{value:.3f}")
                        
                        # Đặt màu xanh cho input đã lưu
                        input_widget.setStyleSheet("""
                            QLineEdit {
                                border: 2px solid #4caf50;
                                border-radius: 6px;
                                padding: 8px;
                                background: #f1f8e9;
                                font-size: 14px;
                            }
                        """)
                        input_widget.setEnabled(False)  # Disable input đã lưu
                        
                        # Chuyển sang thông số tiếp theo
                        self.current_param_index += 1
                        
                        if self.current_param_index < len(self.parameters_list):
                            # Còn thông số tiếp theo
                            self.update_current_parameter_display()
                            self.status_label.setText(f"✅ Đã lưu {current_param['name']} = {value} - Chuyển sang thông số tiếp theo")
                        else:
                            # Đã hoàn thành tất cả thông số
                            self.status_label.setText("🎉 Đã hoàn thành đo tất cả thông số!")
                            self.start_btn.setText("Đo sản phẩm mới")
                            self.start_btn.clicked.disconnect()
                            self.start_btn.clicked.connect(self.reset_for_new_product)
                    else:
                        self.status_label.setText("❌ Lỗi lưu dữ liệu vào database")
                        
                except ValueError:
                    self.status_label.setText(f"❌ Giá trị '{value_text}' không hợp lệ cho {current_param['name']}")
                    input_widget.setStyleSheet("""
                        QLineEdit {
                            border: 2px solid #f44336;
                            border-radius: 6px;
                            padding: 8px;
                            background: #ffebee;
                            font-size: 14px;
                        }
                    """)
            else:
                self.status_label.setText(f"⚠️ Vui lòng nhập giá trị cho {current_param['name']}")
    
    def reset_for_new_product(self):
        """Reset để đo sản phẩm mới"""
        self.current_param_index = 0
        
        # Clear tất cả inputs và enable lại
        for param_id, input_widget in self.manual_inputs.items():
            input_widget.clear()
            input_widget.setEnabled(True)
            input_widget.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #e53935;
                    border-radius: 6px;
                    padding: 8px;
                    background: #fef2f2;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #b71c1c;
                    background: white;
                }
            """)
        
        # Reset displays
        for label in self.param_labels.values():
            label.setText("--")
            
        # Reset button
        self.start_btn.setText("Lưu giá trị")
        self.start_btn.clicked.disconnect()
        self.start_btn.clicked.connect(self.start_measurement)
        
        # Update display
        self.update_current_parameter_display()

    def scan_devices(self):
        """Quét thiết bị COM có sẵn"""
        self.device_list.clear()
        
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            
            if not ports:
                self.device_list.addItem("Không tìm thấy thiết bị nào")
                self.connect_btn.setEnabled(False)
                # Tự động enable manual mode khi không có thiết bị
                self.toggle_manual_mode()
                self.status_label.setText("Không có thiết bị - đã chuyển sang chế độ nhập thủ công")
            else:
                for port in ports:
                    item_text = f"{port.device} - {port.description}"
                    self.device_list.addItem(item_text)
                self.connect_btn.setEnabled(True)
                self.status_label.setText(f"Tìm thấy {len(ports)} thiết bị")
                
        except ImportError as e:
            print(f"Debug: Cannot import serial: {e}")
            self.device_list.addItem("Lỗi: Không thể import serial")
            self.connect_btn.setEnabled(False)
            # Tự động enable manual mode khi có lỗi
            self.toggle_manual_mode()
            self.status_label.setText("Pyserial chưa cài đặt - đã chuyển sang chế độ nhập thủ công")
        except Exception as e:
            print(f"Debug: Error scanning devices: {e}")
            self.device_list.addItem("Lỗi quét thiết bị")
            self.connect_btn.setEnabled(False)
            # Tự động enable manual mode khi có lỗi
            self.toggle_manual_mode()
            self.status_label.setText(f"Lỗi quét thiết bị - đã chuyển sang chế độ nhập thủ công")

    def connect_device(self):
        """Kết nối với thiết bị được chọn"""
        current_item = self.device_list.currentItem()
        if not current_item or "Không tìm thấy" in current_item.text():
            return
            
        try:
            port = current_item.text().split(' - ')[0]
            self.device = HighGaugeDevice()
            
            if self.device.connect(port):
                self.status_label.setText(f"Đã kết nối: {port}")
                self.connect_btn.setText("Ngắt kết nối")
                self.connect_btn.clicked.disconnect()
                self.connect_btn.clicked.connect(self.disconnect_device)
                self.start_btn.setEnabled(True)
                self.manual_btn.setEnabled(False)
            else:
                self.status_label.setText("Không thể kết nối thiết bị")
        except Exception as e:
            self.status_label.setText(f"Lỗi kết nối: {str(e)}")

    def disconnect_device(self):
        """Ngắt kết nối thiết bị"""
        if self.device:
            self.device.disconnect()
            self.device = None
            
        self.status_label.setText("Đã ngắt kết nối")
        self.connect_btn.setText("Kết nối thiết bị")
        self.connect_btn.clicked.disconnect()
        self.connect_btn.clicked.connect(self.connect_device)
        self.start_btn.setEnabled(False)
        self.manual_btn.setEnabled(True)
        self.measurement_timer.stop()

    def toggle_manual_mode(self):
        """Chuyển đổi chế độ nhập thủ công"""
        is_manual = not self.manual_widget.isVisible()
        self.manual_widget.setVisible(is_manual)
        
        # Show/hide manual inputs
        for input_widget in self.manual_inputs.values():
            input_widget.setVisible(is_manual)
            if is_manual:
                # Set placeholder và focus cho input
                input_widget.setPlaceholderText("Nhập giá trị...")
                input_widget.setStyleSheet("""
                    QLineEdit {
                        border: 2px solid #e53935;
                        border-radius: 6px;
                        padding: 8px;
                        background: #fef2f2;
                        font-size: 14px;
                    }
                    QLineEdit:focus {
                        border: 2px solid #b71c1c;
                        background: white;
                    }
                """)
            else:
                input_widget.setStyleSheet("")
                
        # Focus vào input đầu tiên khi chuyển sang manual mode
        if is_manual and self.manual_inputs:
            first_input = list(self.manual_inputs.values())[0]
            first_input.setFocus()
            
        if is_manual:
            self.manual_btn.setText("Hủy nhập thủ công")
            self.start_btn.setEnabled(True)
            self.start_btn.setText("Lưu giá trị")
            self.status_label.setText("✏️ Chế độ nhập thủ công - nhập giá trị và bấm 'Lưu giá trị'")
        else:
            self.manual_btn.setText("Nhập thủ công")
            self.start_btn.setEnabled(self.device is not None)
            self.start_btn.setText("Bắt đầu đo")
            if self.device:
                self.status_label.setText("🔧 Đã sẵn sàng đo tự động")
            else:
                self.status_label.setText("⚠️ Chưa kết nối thiết bị")

    def start_measurement(self):
        """Bắt đầu đo lường"""
        if self.manual_widget.isVisible():
            # Manual mode - save current parameter
            self.save_current_parameter()
        else:
            # Device mode
            if self.device and self.device.is_device_connected():
                self.measurement_timer.start(1000)  # Read every second
                self.start_btn.setText("Dừng đo")
                self.start_btn.clicked.disconnect()
                self.start_btn.clicked.connect(self.stop_measurement)
                self.status_label.setText("Đang đo...")

    def stop_measurement(self):
        """Dừng đo lường"""
        self.measurement_timer.stop()
        self.start_btn.setText("Bắt đầu đo")
        self.start_btn.clicked.disconnect()
        self.start_btn.clicked.connect(self.start_measurement)
        self.status_label.setText("Đã dừng đo")

    def read_measurement(self):
        """Đọc giá trị từ thiết bị"""
        if self.device and self.device.is_device_connected():
            try:
                value = self.device.read_data()
                if value is not None:
                    # Update first parameter (assuming single parameter for now)
                    if self.param_labels:
                        first_param_id = list(self.param_labels.keys())[0]
                        self.param_labels[first_param_id].setText(f"{value:.3f}")
                        self.current_values[first_param_id] = value
                        self.save_btn.setEnabled(True)
            except Exception as e:
                self.status_label.setText(f"Lỗi đọc dữ liệu: {str(e)}")

    def read_manual_values(self):
        """Đọc giá trị nhập thủ công"""
        try:
            values_count = 0
            errors = []
            
            for param_id, input_widget in self.manual_inputs.items():
                value_text = input_widget.text().strip()
                if value_text:
                    try:
                        value = float(value_text)
                        self.param_labels[param_id].setText(f"{value:.3f}")
                        self.current_values[param_id] = value
                        values_count += 1
                        # Đặt màu xanh cho input hợp lệ
                        input_widget.setStyleSheet("""
                            QLineEdit {
                                border: 2px solid #4caf50;
                                border-radius: 6px;
                                padding: 8px;
                                background: #f1f8e9;
                                font-size: 14px;
                            }
                        """)
                    except ValueError:
                        errors.append(f"Thông số {param_id}")
                        # Đặt màu đỏ cho input lỗi
                        input_widget.setStyleSheet("""
                            QLineEdit {
                                border: 2px solid #f44336;
                                border-radius: 6px;
                                padding: 8px;
                                background: #ffebee;
                                font-size: 14px;
                            }
                        """)
                else:
                    # Chưa nhập - màu cam
                    input_widget.setStyleSheet("""
                        QLineEdit {
                            border: 2px solid #ff9800;
                            border-radius: 6px;
                            padding: 8px;
                            background: #fff3e0;
                            font-size: 14px;
                        }
                    """)
            
            if errors:
                self.status_label.setText(f"❌ Lỗi: {', '.join(errors)} có giá trị không hợp lệ")
            elif values_count == 0:
                self.status_label.setText("⚠️ Vui lòng nhập ít nhất một giá trị")
            else:
                self.save_btn.setEnabled(True)
                self.status_label.setText(f"✅ Đã nhập {values_count} giá trị thành công - có thể lưu")
                
        except Exception as e:
            self.status_label.setText(f"❌ Lỗi: {str(e)}")

    def save_measurement(self):
        """Lưu kết quả đo"""
        if not self.current_values:
            self.status_label.setText("Chưa có dữ liệu để lưu")
            return
            
        try:
            # Save to database
            for param_id, value in self.current_values.items():
                self.measurement_manager.add_measurement(
                    model_id=self.model_id,
                    parameter_id=param_id,
                    value=value
                )
            
            self.status_label.setText("Đã lưu kết quả thành công")
            self.save_btn.setEnabled(False)
            
            # Clear values for next measurement
            self.current_values.clear()
            for label in self.param_labels.values():
                label.setText("--")
            for input_widget in self.manual_inputs.values():
                input_widget.clear()
                
        except Exception as e:
            self.status_label.setText(f"Lỗi lưu dữ liệu: {str(e)}")

    def closeEvent(self, event):
        """Xử lý khi đóng dialog"""
        if self.device:
            self.device.disconnect()
        self.measurement_timer.stop()
        event.accept()

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._animation = QPropertyAnimation(self, b"pos")
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.setDuration(150)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background: #e53935;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #b71c1c;
            }
        """)
        
    def mousePressEvent(self, event):
        print(f"Debug: ModernButton clicked: {self.text()}")
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self._animation.setStartValue(self.pos())
        self._animation.setEndValue(self.pos() + QPoint(0, -2))
        self._animation.start()

    def leaveEvent(self, event):
        self._animation.setStartValue(self.pos())
        self._animation.setEndValue(self.pos() + QPoint(0, 2))
        self._animation.start()

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

class DashboardWidget(QWidget):
    def __init__(self, parent=None, model_id=None):
        super().__init__(parent)
        # Thêm bảng màu xanh-đỏ
        self.colors = {
            'primary': '#e53935',      # Đỏ chính
            'primary_dark': '#b71c1c',
            'blue': '#2563eb',         # Xanh chính
            'blue_light': '#3b82f6',
            'blue_bg': '#eff6ff',
            'gray': '#6b7280',
            'border': '#e5e7eb',
            'white': '#ffffff'
        }
        self.dashboard_manager = DashboardManager()
        self.model_manager = ModelManager()
        self.current_model_id = model_id
        self.current_parameter = None
        # StyleSheet mới - bỏ background của labels
        self.setStyleSheet(f"""
            QWidget {{
                background: #f5f6fa;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}
            QFrame#header {{
                background: #fff;
                border-bottom: 1px solid #e5e7eb;
                box-shadow: 0 1px 4px rgba(0,0,0,0.04);
                padding: 18px 24px;
            }}
            QFrame#main_card {{
                background: #fff;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
                box-shadow: 0 1px 4px rgba(0,0,0,0.04);
                padding: 18px 24px;
            }}
            QLabel#card_title {{
                font-size: 17px;
                font-weight: 600;
                color: #2563eb;
                margin-bottom: 8px;
                background: transparent;
            }}
            QLabel#title {{
                font-size: 22px;
                font-weight: 700;
                color: {self.colors['primary']};
                margin-bottom: 4px;
                background: transparent;
            }}
            QLabel#subtitle {{
                font-size: 15px;
                color: #2563eb;
                font-weight: 600;
                background: transparent;
            }}
            QLabel {{
                background: transparent;
            }}
            QLabel#image_label {{
                border-radius: 10px;
                padding: 8px;
                border: 2px dashed #e5e7eb;
            }}
            QPushButton#measure_btn {{
                background: #e53935;
                color: #fff;
                border-radius: 8px;
                font-size: 16px;
                padding: 10px 28px;
                font-weight: 600;
            }}
            QPushButton#measure_btn:hover {{
                background: #2563eb;
            }}
            QPushButton {{
                background: #2563eb;
                color: white;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: #e53935;
            }}
            QComboBox {{
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 4px 10px;
                background: #fff;
                color: #2563eb;
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                width: 10px;
                height: 10px;
                margin-right: 4px;
            }}
            QTableWidget {{
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background: #fff;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 6px;
                border-radius: 6px;
            }}
            QTableWidget::item:selected {{
                background: #eff6ff;
                color: #2563eb;
            }}
            QTableWidget::item:hover {{
                background: #eff6ff;
            }}
            QHeaderView::section {{
                background: #f5f6fa;
                color: #2563eb;
                font-weight: 600;
                font-size: 13px;
                border: none;
                border-bottom: 1px solid #e5e7eb;
            }}
        """)
        self.init_ui()
        print("Debug: Connecting measure button...")
        self.measure_btn.clicked.connect(self.show_measurement_dialog)
        print("Debug: Button connected successfully")
        
        # Test nếu có model_id
        if model_id:
            self.set_model(model_id)
        else:
            # Nếu không có model_id, thử lấy model đầu tiên
            try:
                models = self.model_manager.get_all_models()
                if models:
                    print(f"Debug: Setting first model: {models[0]['id']}")
                    self.set_model(models[0]['id'])
            except Exception as e:
                print(f"Debug: Error getting models: {e}")

    def create_divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background: #e5e7eb; min-height:1px; max-height:1px;")
        return line

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("header")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(12)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_left = QVBoxLayout()
        self.model_name_label = ClickableLabel("Tên Model")
        self.model_name_label.setObjectName("title")
        self.model_name_label.clicked.connect(self.show_model_selector)
        header_left.addWidget(self.model_name_label)
        self.total_label = QLabel("Tổng sản phẩm: 0")
        self.total_label.setObjectName("subtitle")
        header_left.addWidget(self.total_label)
        header_layout.addLayout(header_left)
        self.measure_btn = ModernButton("Bắt đầu đo")
        self.measure_btn.setObjectName("measure_btn")
        header_layout.addWidget(self.measure_btn, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(header_frame)

        # Main content section
        content_layout = QHBoxLayout()
        content_layout.setSpacing(18)
        # Left: Model image
        left_card = QFrame()
        left_card.setObjectName("main_card")
        left_layout = QVBoxLayout(left_card)
        image_title = QLabel("Hình ảnh Model")
        image_title.setObjectName("card_title")
        left_layout.addWidget(image_title)
        self.image_label = QLabel()
        self.image_label.setObjectName("image_label")
        self.image_label.setFixedSize(320, 320)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.image_label)
        content_layout.addWidget(left_card)
        # Right: Chart
        right_card = QFrame()
        right_card.setObjectName("main_card")
        right_layout = QVBoxLayout(right_card)
        chart_header = QHBoxLayout()
        chart_title = QLabel("Biểu đồ thông số")
        chart_title.setObjectName("card_title")
        chart_header.addWidget(chart_title)
        param_layout = QHBoxLayout()
        param_label = QLabel("Chọn thông số:")
        param_label.setObjectName("subtitle")
        param_layout.addWidget(param_label)
        self.param_combo = QComboBox()
        self.param_combo.currentIndexChanged.connect(self.update_chart)
        param_layout.addWidget(self.param_combo)
        chart_header.addLayout(param_layout)
        right_layout.addLayout(chart_header)
        self.figure, self.ax = plt.subplots()
        self.figure.patch.set_facecolor(self.colors['white'])
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setObjectName("chart_canvas")
        right_layout.addWidget(self.canvas)
        content_layout.addWidget(right_card)
        main_layout.addLayout(content_layout)

        # History section
        history_card = QFrame()
        history_card.setObjectName("main_card")
        history_layout = QVBoxLayout(history_card)
        history_title = QLabel("Lịch sử đo các sản phẩm")
        history_title.setObjectName("card_title")
        history_layout.addWidget(history_title)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(0)
        self.history_table.setRowCount(0)
        self.history_table.setAlternatingRowColors(True)
        history_layout.addWidget(self.history_table)
        main_layout.addWidget(history_card)

    def show_model_selector(self, event=None):
        models = self.model_manager.get_all_models()
        dialog = ModelSelectorDialog(models, current_model_id=self.current_model_id, parent=self)
        if dialog.exec():
            selected_id = dialog.get_selected_model_id()
            if selected_id and selected_id != self.current_model_id:
                self.set_model(selected_id)

    def set_model(self, model_id):
        self.current_model_id = model_id
        model = self.model_manager.get_model_by_id(model_id)
        if model:
            self.model_name_label.setText(model['name'])
            if model.get('image_path') and os.path.exists(model['image_path']):
                pixmap = QPixmap(model['image_path'])
                self.image_label.setPixmap(pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
            else:
                self.image_label.setPixmap(QPixmap())
            total = self.dashboard_manager.get_total_product(model_id)
            self.total_label.setText(f"Tổng sản phẩm: {total}")
            params = self.dashboard_manager.get_parameters_by_model(model_id)
            self.param_combo.clear()
            for p in params:
                self.param_combo.addItem(f"{p['name']} ({p['unit']})", p['id'])
            if params:
                self.current_parameter = params[0]['id']
                self.update_chart()
            self.load_history()

    def update_chart(self):
        param_id = self.param_combo.currentData()
        if not param_id:
            return
        data = self.dashboard_manager.get_measurement_data(param_id)
        self.ax.clear()
        if not data.empty:
            # Tạo trục x theo số sản phẩm (1, 2, 3, ...)
            product_numbers = list(range(1, len(data) + 1))
            self.ax.plot(product_numbers, data['value'], marker='o', color='#e53935', linewidth=2.5)
            self.ax.set_title(f"Biểu đồ thông số {self.param_combo.currentText()}", 
                            pad=24, fontsize=14, color='#b71c1c', fontweight='600')
            self.ax.set_xlabel("Số sản phẩm", color='#e53935', fontsize=12)
            self.ax.set_ylabel("Giá trị", color='#e53935', fontsize=12)
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            self.ax.tick_params(colors='#e53935')
            
            # Đặt x ticks cho số nguyên
            self.ax.set_xticks(product_numbers)
        self.canvas.draw()

    def load_history(self):
        """Load lịch sử đo của model hiện tại"""
        if not self.current_model_id:
            return
            
        history = self.dashboard_manager.get_history_by_model(self.current_model_id)
        
        if not history:
            # Xóa table nếu không có dữ liệu
            self.history_table.setRowCount(0)
            self.history_table.setColumnCount(0)
            return
            
        # Lấy tất cả keys từ record đầu tiên để làm headers
        if history:
            all_keys = list(history[0].keys())
            
            # Tạo headers: STT, Thời gian, và các thông số
            headers = []
            for key in all_keys:
                if key == 'STT':
                    headers.append('STT')
                elif key == 'measured_at':
                    headers.append('Thời gian')
                else:
                    # Đây là tên thông số (đã có unit)
                    headers.append(key)
            
            # Set up table
            self.history_table.setRowCount(len(history))
            self.history_table.setColumnCount(len(headers))
            self.history_table.setHorizontalHeaderLabels(headers)
            
            # Populate data
            for row_idx, product in enumerate(history):
                for col_idx, key in enumerate(all_keys):
                    if key == 'measured_at':
                        # Format thời gian đẹp hơn
                        time_str = product[key].strftime('%Y-%m-%d %H:%M:%S')
                        item = QTableWidgetItem(time_str)
                    else:
                        item = QTableWidgetItem(str(product[key]))
                    
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.history_table.setItem(row_idx, col_idx, item)
            
            # Auto resize columns
            self.history_table.resizeColumnsToContents()
            
            # Đặt độ rộng tối thiểu cho cột đầu
            if self.history_table.columnCount() > 0:
                self.history_table.setColumnWidth(0, 50)  # STT column

    def show_measurement_dialog(self):
        print(f"Debug: show_measurement_dialog called, current_model_id = {self.current_model_id}")
        
        if not self.current_model_id:
            # Nếu chưa có model nào được chọn, hiển thị thông báo
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Thông báo", 
                "Vui lòng chọn model trước khi bắt đầu đo lường!\n"
                "Nhấp vào tên model ở trên để chọn.")
            return
        
        try:
            print(f"Debug: Creating MeasurementDialog for model_id = {self.current_model_id}")
            dialog = MeasurementDialog(self.current_model_id, self)
            print("Debug: MeasurementDialog created successfully, showing...")
            dialog.exec()
            print("Debug: Dialog closed")
            
            # Sau khi đo xong có thể reload lại dashboard nếu cần
            self.set_model(self.current_model_id)
        except Exception as e:
            print(f"Debug: Error creating/showing dialog: {e}")
            import traceback
            traceback.print_exc()
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Lỗi", f"Không thể mở dialog đo lường: {str(e)}")



class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        # Định nghĩa các màu
        self.colors = {
            'primary': '#dc2626',      # Đỏ chính
            'primary_light': '#ef4444', # Đỏ nhạt
            'primary_lighter': '#fecaca', # Đỏ rất nhạt
            'primary_bg': '#fef2f2',   # Nền đỏ nhạt
            'primary_dark': '#991b1b', # Đỏ đậm
            'white': '#ffffff',        # Trắng
            'gray': '#6b7280',         # Xám
            'border': '#e5e7eb'        # Màu viền
        }
        
        # Xóa cache của Plotly
        pio.templates.default = "plotly_white"
        
        self.setStyleSheet(f"""
            QWidget {{
                background: {self.colors['white']};
                font-family: 'Segoe UI', sans-serif;
            }}
            QLabel {{
                color: {self.colors['primary_dark']};
            }}
            QComboBox {{
                border: 1px solid {self.colors['border']};
                border-radius: 4px;
                padding: 4px 8px;
                background: {self.colors['white']};
                min-width: 150px;
                color: {self.colors['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                width: 10px;
                height: 10px;
                margin-right: 4px;
            }}
            QLabel#model_name {{
                font-size: 16px;
                font-weight: bold;
                color: {self.colors['primary']};
                padding: 4px 8px;
            }}
            QFrame#header {{
                background: {self.colors['primary_bg']};
                border-bottom: 1px solid {self.colors['border']};
            }}
            QFrame#overview {{
                background: {self.colors['white']};
                border-bottom: 1px solid {self.colors['border']};
            }}
            QFrame#chart_container {{
                background: {self.colors['white']};
            }}
            QLabel#overview_title {{
                color: {self.colors['primary']};
                font-size: 14px;
                font-weight: bold;
            }}
            QLabel#overview_value {{
                color: {self.colors['primary_dark']};
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        self.init_ui()
        
    def init_ui(self):
        # Layout chính
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header với model selector
        header_frame = QFrame()
        header_frame.setObjectName("header")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 12, 16, 12)
        header_layout.setSpacing(8)
        
        model_label = QLabel("Model:")
        model_label.setStyleSheet(f"font-weight: bold; color: {self.colors['primary']};")
        
        self.model_name = ClickableLabel("Model A")
        self.model_name.setObjectName("model_name")
        self.model_name.clicked.connect(self.show_model_selector)
        
        self.model_selector = QComboBox()
        self.model_selector.addItems([m['name'] for m in self.model_manager.get_all_models()])
        self.model_selector.currentIndexChanged.connect(self.on_model_selected)
        self.model_selector.hide()
        
        header_layout.addWidget(model_label)
        header_layout.addWidget(self.model_name)
        header_layout.addWidget(self.model_selector)
        header_layout.addStretch()
        
        # Thông tin tổng quan
        overview_frame = QFrame()
        overview_frame.setObjectName("overview")
        overview_layout = QGridLayout(overview_frame)
        overview_layout.setContentsMargins(16, 12, 16, 12)
        overview_layout.setSpacing(16)
        
        # Tạo các ô thông tin
        overview_items = [
            ("Tổng số mẫu", "1,234"),
            ("Mẫu lỗi", "23"),
            ("Tỷ lệ lỗi", "1.86%"),
            ("Thời gian chạy", "2h 30m")
        ]
        
        for i, (title, value) in enumerate(overview_items):
            title_label = QLabel(title)
            title_label.setObjectName("overview_title")
            value_label = QLabel(value)
            value_label.setObjectName("overview_value")
            
            overview_layout.addWidget(title_label, 0, i)
            overview_layout.addWidget(value_label, 1, i)
        
        # Biểu đồ
        chart_frame = QFrame()
        chart_frame.setObjectName("chart_container")
        chart_layout = QHBoxLayout(chart_frame)
        chart_layout.setContentsMargins(16, 12, 16, 12)
        chart_layout.setSpacing(16)
        
        # Biểu đồ thông số
        self.params_chart = PlotWidget()
        self.update_params_chart()
        chart_layout.addWidget(self.params_chart)
        
        # Biểu đồ lỗi
        self.error_chart = PlotWidget()
        self.update_error_chart()
        chart_layout.addWidget(self.error_chart)
        
        # Thêm tất cả vào layout chính
        main_layout.addWidget(header_frame)
        main_layout.addWidget(overview_frame)
        main_layout.addWidget(chart_frame)
        
        self.setLayout(main_layout)
        
    def show_model_selector(self):
        self.model_name.hide()
        self.model_selector.show()
        self.model_selector.setFocus()
        self.model_selector.showPopup()
        
    def on_model_selected(self, index):
        model_name = self.model_selector.currentText()
        model_id = self.model_manager.get_all_models()[index]['id']
        self.update_dashboard(model_id)
        
    def update_params_chart(self):
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)
        
        fig = make_subplots(rows=2, cols=1, subplot_titles=("Thông số 1", "Thông số 2"))
        
        fig.add_trace(go.Scatter(x=x, y=y1, name="Thông số 1", line=dict(color=self.colors['primary'])), row=1, col=1)
        fig.add_trace(go.Scatter(x=x, y=y2, name="Thông số 2", line=dict(color=self.colors['primary_light'])), row=2, col=1)
        
        fig.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False,
            template="plotly_white",
            paper_bgcolor=self.colors['white'],
            plot_bgcolor=self.colors['white'],
            font=dict(color=self.colors['primary_dark'])
        )
        
        self.params_chart.update_plot(fig)
        
    def update_error_chart(self):
        dates = [datetime.now() - timedelta(days=i) for i in range(7)]
        errors = [10, 15, 8, 12, 9, 11, 13]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=dates,
            y=errors,
            name="Số lỗi",
            marker_color=self.colors['primary']
        ))
        
        fig.update_layout(
            title="Biểu đồ lỗi theo thời gian",
            height=400,
            margin=dict(l=10, r=10, t=30, b=10),
            template="plotly_white",
            paper_bgcolor=self.colors['white'],
            plot_bgcolor=self.colors['white'],
            font=dict(color=self.colors['primary_dark'])
        )
        
        self.error_chart.update_plot(fig)

    def update_dashboard(self, model_id):
        # Lấy thông tin model, hình ảnh, tổng số sản phẩm đã đo, v.v.
        model = self.model_manager.get_model_by_id(model_id)
        # Cập nhật các widget: tên, hình, biểu đồ, bảng lịch sử đo...
        # Ví dụ: self.model_name.setText(f"Model đang chọn: {model['name']}")
        # Cập nhật hình ảnh, biểu đồ, bảng lịch sử đo...
        self.set_model(model_id)
        self.model_name.setText(model['name'])
        if model.get('image_path') and os.path.exists(model['image_path']):
            pixmap = QPixmap(model['image_path'])
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.image_label.setPixmap(QPixmap())
        total = self.dashboard_manager.get_total_product(model_id)
        self.total_label.setText(f"Tổng sản phẩm: {total}")
        params = self.dashboard_manager.get_parameters_by_model(model_id)
        self.param_combo.clear()
        for p in params:
            self.param_combo.addItem(f"{p['name']} ({p['unit']})", p['id'])
        if params:
            self.current_parameter = params[0]['id']
            self.update_chart()
        self.load_history()
        self.reload_model_combo() 