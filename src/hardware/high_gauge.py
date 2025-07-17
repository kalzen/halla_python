import serial
import time
from PyQt6.QtCore import QObject, pyqtSignal

# Import config modules
try:
    from config.database import DatabaseConfig
except ImportError:
    try:
        from src.config.database import DatabaseConfig
    except ImportError:
        from ..config.database import DatabaseConfig

class HighGaugeDevice(QObject):
    # Signal khi nhận được dữ liệu từ thiết bị
    data_received = pyqtSignal(float)
    # Signal khi có lỗi kết nối
    connection_error = pyqtSignal(str)
    # Signal khi kết nối thành công
    connected = pyqtSignal()
    # Signal khi ngắt kết nối
    disconnected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.is_connected = False
        self.is_reading = False

    def connect(self, port, baudrate=9600):
        """Kết nối với thiết bị qua cổng COM"""
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            self.is_connected = True
            self.connected.emit()
            return True
        except Exception as e:
            self.connection_error.emit(f"Lỗi kết nối: {str(e)}")
            return False

    def disconnect(self):
        """Ngắt kết nối với thiết bị"""
        if self.serial_port and self.serial_port.is_open:
            self.stop_reading()
            self.serial_port.close()
            self.is_connected = False
            self.disconnected.emit()

    def start_reading(self):
        """Bắt đầu đọc dữ liệu từ thiết bị"""
        if not self.is_connected:
            self.connection_error.emit("Chưa kết nối với thiết bị")
            return False

        self.is_reading = True
        try:
            # Gửi lệnh bắt đầu đo
            self.serial_port.write(b'START\n')
            return True
        except Exception as e:
            self.connection_error.emit(f"Lỗi khi bắt đầu đọc: {str(e)}")
            return False

    def stop_reading(self):
        """Dừng đọc dữ liệu từ thiết bị"""
        if self.is_connected:
            try:
                # Gửi lệnh dừng đo
                self.serial_port.write(b'STOP\n')
            except Exception as e:
                self.connection_error.emit(f"Lỗi khi dừng đọc: {str(e)}")
        self.is_reading = False

    def read_data(self):
        """Đọc dữ liệu từ thiết bị"""
        if not self.is_connected or not self.is_reading:
            return None

        try:
            if self.serial_port.in_waiting:
                data = self.serial_port.readline().decode().strip()
                try:
                    value = float(data)
                    self.data_received.emit(value)
                    return value
                except ValueError:
                    self.connection_error.emit("Dữ liệu không hợp lệ")
                    return None
        except Exception as e:
            self.connection_error.emit(f"Lỗi khi đọc dữ liệu: {str(e)}")
            return None

    def get_available_ports(self):
        """Lấy danh sách các cổng COM có sẵn"""
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def is_device_connected(self):
        """Kiểm tra trạng thái kết nối"""
        return self.is_connected and self.serial_port and self.serial_port.is_open 