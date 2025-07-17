import os
import sys
import mysql.connector
import traceback
import time

# Load dotenv only if available
try:
    from dotenv import load_dotenv
    # Tìm file .env trong executable path
    if hasattr(sys, '_MEIPASS'):
        # Running in PyInstaller bundle
        env_path = os.path.join(sys._MEIPASS, '.env')
    else:
        # Running normally
        env_path = '.env'
    
    if os.path.exists(env_path):
        try:
            load_dotenv(env_path)
            print(f"[INFO] Loaded .env from: {env_path}")
        except UnicodeDecodeError:
            print(f"[WARNING] .env file has encoding issues, using default config")
        except Exception as e:
            print(f"[WARNING] Could not load .env: {e}")
except ImportError:
    print("[INFO] python-dotenv not available, using default config")

class DatabaseConfig:
    # Database configuration với giá trị mặc định
    # Ưu tiên environment variables, fallback về config cố định
    HOST = os.getenv('DB_HOST') or 'localhost'
    USER = os.getenv('DB_USER') or 'root'
    PASSWORD = os.getenv('DB_PASSWORD') or ''  # Cho phép mật khẩu trống
    DATABASE = os.getenv('DB_NAME') or 'halla'
    PORT = int(os.getenv('DB_PORT') or '3306')

    @staticmethod
    def get_connection():
        try:
            print("\n=== BẮT ĐẦU KẾT NỐI DATABASE ===")
            print(f"Running from: {sys.executable}")
            print(f"Is PyInstaller: {hasattr(sys, '_MEIPASS')}")
            if hasattr(sys, '_MEIPASS'):
                print(f"PyInstaller temp dir: {sys._MEIPASS}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Thông tin kết nối:")
            print(f"- Host: {DatabaseConfig.HOST}")
            print(f"- User: {DatabaseConfig.USER}")
            print(f"- Database: {DatabaseConfig.DATABASE}")
            print(f"- Port: {DatabaseConfig.PORT}")
            print(f"- Password: {'[CÓ]' if DatabaseConfig.PASSWORD else '[TRỐNG]'}")
            
            print("\nĐang thử kết nối...")
            # Thử kết nối với các tùy chọn khác
            print("Thử kết nối với caching_sha2_password...")
            try:
                connection = mysql.connector.connect(
                    host=DatabaseConfig.HOST,
                    user=DatabaseConfig.USER,
                    password=DatabaseConfig.PASSWORD,
                    database=DatabaseConfig.DATABASE,
                    port=DatabaseConfig.PORT,
                    use_pure=True,  # Sử dụng pure Python implementation
                    connect_timeout=10,  # Timeout 10 giây
                    auth_plugin='caching_sha2_password',
                    charset='utf8mb4',
                    collation='utf8mb4_unicode_ci'
                )
            except mysql.connector.Error as e:
                print(f"Lỗi với caching_sha2_password: {e}")
                print("Thử kết nối không chỉ định auth_plugin...")
                connection = mysql.connector.connect(
                    host=DatabaseConfig.HOST,
                    user=DatabaseConfig.USER,
                    password=DatabaseConfig.PASSWORD,
                    database=DatabaseConfig.DATABASE,
                    port=DatabaseConfig.PORT,
                    use_pure=True,
                    connect_timeout=10,
                    charset='utf8mb4',
                    collation='utf8mb4_unicode_ci'
                )
            
            print("\nĐang kiểm tra trạng thái kết nối...")
            if connection.is_connected():
                print("Đã kết nối thành công đến MySQL Server")
                cursor = connection.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"MySQL Server version: {version[0]}")
                cursor.close()
                print("=== KẾT NỐI DATABASE THÀNH CÔNG ===\n")
                return connection
            else:
                print("=== KẾT NỐI DATABASE THẤT BẠI: Không thể xác nhận kết nối ===\n")
                return None
                
        except mysql.connector.Error as err:
            print("\n=== LỖI KẾT NỐI MYSQL ===")
            print(f"Error Code: {err.errno}")
            print(f"Error Message: {err.msg}")
            print(traceback.format_exc())
            print("=== KẾT THÚC BÁO LỖI ===\n")
            return None
        except Exception as e:
            print("\n=== LỖI KHÔNG XÁC ĐỊNH ===")
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            print("=== KẾT THÚC BÁO LỖI ===\n")
            return None

    def init_database(self):
        """Khởi tạo các bảng trong database nếu chưa tồn tại"""
        connection = self.get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                
                # Tạo bảng models
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS models (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Tạo bảng parameters
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS parameters (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        model_id INT,
                        name VARCHAR(100) NOT NULL,
                        unit VARCHAR(50),
                        min_value FLOAT,
                        max_value FLOAT,
                        FOREIGN KEY (model_id) REFERENCES models(id)
                    )
                """)

                # Tạo bảng measurements
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS measurements (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        parameter_id INT,
                        value FLOAT NOT NULL,
                        device_id VARCHAR(100),
                        measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (parameter_id) REFERENCES parameters(id)
                    )
                """)

                # Tạo bảng templates
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS templates (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        name VARCHAR(100) NOT NULL,
                        file_path VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                connection.commit()
                print("Khởi tạo database thành công!")
            except Error as e:
                print(f"Lỗi khởi tạo database: {e}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close() 