# Import config modules
try:
    from config.database import DatabaseConfig
except ImportError:
    try:
        from src.config.database import DatabaseConfig
    except ImportError:
        from ..config.database import DatabaseConfig

class ParameterManager:
    def __init__(self):
        self.db_config = DatabaseConfig()

    def get_parameters_by_model(self, model_id):
        """Lấy danh sách thông số của một model"""
        connection = self.db_config.get_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    "SELECT * FROM parameters WHERE model_id = %s ORDER BY name",
                    (model_id,)
                )
                return cursor.fetchall()
            except Exception as e:
                print(f"Lỗi khi lấy danh sách thông số: {e}")
                return []
            finally:
                cursor.close()
                connection.close()
        return [] 