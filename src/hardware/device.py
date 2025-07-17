import serial
import serial.tools.list_ports
from PyQt6.QtCore import QObject, pyqtSignal
import time
from datetime import datetime

class HighGaugeDevice(QObject):
    value_received = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        self.serial = None
        self.connected = False
    
    @staticmethod
    def list_ports():
        """Liệt kê các cổng COM có sẵn"""
        return [port.device for port in serial.tools.list_ports.comports()]
    
    def connect(self, port):
        """Kết nối với thiết bị qua cổng COM"""
        try:
            self.serial = serial.Serial(port, 9600, timeout=1)
            self.connected = True
            return True
        except Exception as e:
            print(f"Lỗi khi kết nối: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Ngắt kết nối với thiết bị"""
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.connected = False
    
    def get_device_info(self):
        """Đọc thông tin thiết bị"""
        if not self.connected or not self.serial:
            return None
            
        try:
            # Gửi lệnh yêu cầu thông tin thiết bị
            self.serial.write(b'INFO\n')
            time.sleep(0.5)  # Đợi thiết bị phản hồi
            
            info = []
            # Đọc thông tin thiết bị
            while self.serial.in_waiting:
                line = self.serial.readline().decode().strip()
                if line:
                    info.append(line)
                    
            if info:
                return "\n".join([
                    "=== THÔNG TIN THIẾT BỊ ===",
                    f"Cổng COM: {self.serial.port}",
                    f"Tốc độ baud: {self.serial.baudrate}",
                    f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "------------------------",
                    *info,
                    "========================="
                ])
            return None
        except Exception as e:
            print(f"Lỗi khi đọc thông tin thiết bị: {e}")
            return None
    
    def start_measurement(self):
        """Bắt đầu đo"""
        if not self.connected or not self.serial:
            return False
        try:
            self.serial.write(b'START\n')
            return True
        except Exception as e:
            print(f"Lỗi khi bắt đầu đo: {e}")
            return False
    
    def stop_measurement(self):
        """Dừng đo"""
        if not self.connected or not self.serial:
            return False
        try:
            self.serial.write(b'STOP\n')
            return True
        except Exception as e:
            print(f"Lỗi khi dừng đo: {e}")
            return False
    
    def read_data(self):
        """Đọc dữ liệu từ thiết bị"""
        if not self.connected or not self.serial:
            return None
        try:
            if self.serial.in_waiting:
                data = self.serial.readline().decode().strip()
                try:
                    value = float(data)
                    self.value_received.emit(value)
                    return value
                except ValueError:
                    return None
        except Exception as e:
            print(f"Lỗi khi đọc dữ liệu: {e}")
            return None 