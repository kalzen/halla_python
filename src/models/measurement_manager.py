# Import config modules
try:
    from config.database import DatabaseConfig
except ImportError:
    try:
        from src.config.database import DatabaseConfig
    except ImportError:
        from ..config.database import DatabaseConfig
from datetime import datetime

class MeasurementManager:
    def __init__(self):
        self.db_config = DatabaseConfig()

    def add_measurement(self, model_id, parameter_id, value):
        """Lưu kết quả đo vào database"""
        connection = self.db_config.get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO measurements (model_id, parameter_id, value, measured_at) VALUES (%s, %s, %s, %s)",
                    (model_id, parameter_id, value, datetime.now())
                )
                connection.commit()
                return cursor.lastrowid
            except Exception as e:
                print(f"Lỗi khi lưu kết quả đo: {e}")
                return None
            finally:
                cursor.close()
                connection.close()
        return None 