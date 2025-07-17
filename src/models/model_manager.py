import mysql.connector

# Import config modules
try:
    from config.database import DatabaseConfig
except ImportError:
    try:
        from src.config.database import DatabaseConfig
    except ImportError:
        from ..config.database import DatabaseConfig

class ModelManager:
    def __init__(self):
        self.db_config = DatabaseConfig()

    def add_model(self, name, description="", image_path=None, template_path=None):
        """Thêm model mới với hình ảnh và template"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO models (name, description, image_path, template_path)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (name, description, image_path, template_path))
            model_id = cursor.lastrowid
            conn.commit()
            return model_id
        except Exception as err:
            print(f"Lỗi khi thêm model: {err}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def add_parameter(self, model_id, name, unit, description="", min_value=None, max_value=None):
        """Thêm thông số mới cho model"""
        try:
            conn = self.db_config.get_connection()
            print("[DEBUG] Đang kết nối tới database:", conn.database)
            cursor = conn.cursor()
            query = """
                INSERT INTO parameters (model_id, name, unit, description, min_value, max_value)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            print("[DEBUG] Thực thi query:", query)
            print("[DEBUG] Với dữ liệu:", (model_id, name, unit, description, min_value, max_value))
            cursor.execute(query, (model_id, name, unit, description, min_value, max_value))
            parameter_id = cursor.lastrowid
            conn.commit()
            print("[DEBUG] Kết quả insert parameter_id:", parameter_id)
            return parameter_id
        except mysql.connector.Error as err:
            print("[ERROR] Lỗi khi thêm thông số:")
            print("[ERROR] Query:", query)
            print("[ERROR] Dữ liệu:", (model_id, name, unit, description, min_value, max_value))
            print("[ERROR] Chi tiết lỗi:", err)
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def get_all_models(self):
        print("Bắt đầu get_all_models trong ModelManager")
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM models ORDER BY name"
            cursor.execute(query)
            models = cursor.fetchall()
            print(f"Truy vấn thành công, số model: {len(models)}")
            return models
        except Exception as err:
            print(f"Lỗi khi lấy danh sách model: {err}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
        print("Kết thúc get_all_models trong ModelManager")

    def get_parameters_by_model(self, model_id):
        """Lấy danh sách thông số của model"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT * FROM parameters 
                WHERE model_id = %s 
                ORDER BY name
            """
            cursor.execute(query, (model_id,))
            parameters = cursor.fetchall()
            
            return parameters
            
        except mysql.connector.Error as err:
            print(f"Lỗi khi lấy danh sách thông số: {err}")
            return []
            
        finally:
            if 'conn' in locals():
                conn.close()

    def update_model(self, model_id, name, description=""):
        """Cập nhật thông tin model"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            query = """
                UPDATE models 
                SET name = %s, description = %s
                WHERE id = %s
            """
            cursor.execute(query, (name, description, model_id))
            
            conn.commit()
            return True
            
        except mysql.connector.Error as err:
            print(f"Lỗi khi cập nhật model: {err}")
            return False
            
        finally:
            if 'conn' in locals():
                conn.close()

    def update_parameter(self, parameter_id, name, unit, description=""):
        """Cập nhật thông tin thông số"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            query = """
                UPDATE parameters 
                SET name = %s, unit = %s, description = %s
                WHERE id = %s
            """
            cursor.execute(query, (name, unit, description, parameter_id))
            
            conn.commit()
            return True
            
        except mysql.connector.Error as err:
            print(f"Lỗi khi cập nhật thông số: {err}")
            return False
            
        finally:
            if 'conn' in locals():
                conn.close()

    def delete_model(self, model_id):
        """Xóa model"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            # Xóa các thông số liên quan
            cursor.execute("DELETE FROM parameters WHERE model_id = %s", (model_id,))
            
            # Xóa model
            cursor.execute("DELETE FROM models WHERE id = %s", (model_id,))
            
            conn.commit()
            return True
            
        except mysql.connector.Error as err:
            print(f"Lỗi khi xóa model: {err}")
            return False
            
        finally:
            if 'conn' in locals():
                conn.close()

    def delete_parameter(self, parameter_id):
        """Xóa thông số"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            query = "DELETE FROM parameters WHERE id = %s"
            cursor.execute(query, (parameter_id,))
            
            conn.commit()
            return True
            
        except mysql.connector.Error as err:
            print(f"Lỗi khi xóa thông số: {err}")
            return False
            
        finally:
            if 'conn' in locals():
                conn.close()

    def get_model_by_id(self, model_id):
        """Lấy thông tin model theo id"""
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM models WHERE id = %s", (model_id,))
            model = cursor.fetchone()
            return model
        except Exception as err:
            print(f"Lỗi khi lấy model: {err}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def get_parameters(self, model_id):
        """Alias cho get_parameters_by_model để tương thích với các nơi gọi cũ"""
        return self.get_parameters_by_model(model_id) 