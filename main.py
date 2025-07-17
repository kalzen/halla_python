import sys
import os

# Thêm thư mục src vào sys.path để có thể import
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from PyQt6.QtWidgets import QApplication

# Import MainWindow với try-except để xử lý các trường hợp khác nhau
try:
    from src.main import MainWindow
except ImportError:
    try:
        import src.main
        MainWindow = src.main.MainWindow
    except ImportError:
        from main import MainWindow

def main():
    print("=== BẮT ĐẦU KHỞI ĐỘNG ỨNG DỤNG ===")
    print(f"Python executable: {sys.executable}")
    print(f"Script path: {__file__}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Is PyInstaller bundle: {hasattr(sys, '_MEIPASS')}")
    if hasattr(sys, '_MEIPASS'):
        print(f"Bundle temp directory: {sys._MEIPASS}")
    
    print("\nBắt đầu tạo QApplication")
    app = QApplication(sys.argv)
    print("Tạo MainWindow")
    window = MainWindow()
    print("Show MainWindow")
    window.show()
    print("Bắt đầu app.exec()")
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 