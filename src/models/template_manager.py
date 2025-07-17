# Import config modules
try:
    from config.database import DatabaseConfig
except ImportError:
    try:
        from src.config.database import DatabaseConfig
    except ImportError:
        from ..config.database import DatabaseConfig
import os
import shutil
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
from datetime import datetime

class TemplateManager:
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.template_dir = "templates/checksheet_templates"

    def add_template(self, name, file_path):
        """Thêm template mới"""
        # Tạo thư mục nếu chưa tồn tại
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)

        # Sao chép file template vào thư mục templates
        template_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(file_path)}"
        template_path = os.path.join(self.template_dir, template_filename)
        shutil.copy2(file_path, template_path)

        # Lưu thông tin template vào database
        connection = self.db_config.get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO templates (name, file_path) VALUES (%s, %s)",
                    (name, template_path)
                )
                connection.commit()
                return cursor.lastrowid
            except Exception as e:
                print(f"Lỗi khi thêm template: {e}")
                # Xóa file đã sao chép nếu có lỗi
                if os.path.exists(template_path):
                    os.remove(template_path)
                return None
            finally:
                cursor.close()
                connection.close()
        return None

    def get_all_templates(self):
        """Lấy danh sách tất cả template"""
        connection = self.db_config.get_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM templates ORDER BY name")
                return cursor.fetchall()
            except Exception as e:
                print(f"Lỗi khi lấy danh sách template: {e}")
                return []
            finally:
                cursor.close()
                connection.close()
        return []

    def delete_template(self, template_id):
        """Xóa template"""
        connection = self.db_config.get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                # Lấy đường dẫn file trước khi xóa
                cursor.execute("SELECT file_path FROM templates WHERE id = %s", (template_id,))
                result = cursor.fetchone()
                if result:
                    file_path = result[0]
                    # Xóa file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    # Xóa record trong database
                    cursor.execute("DELETE FROM templates WHERE id = %s", (template_id,))
                    connection.commit()
                    return True
            except Exception as e:
                print(f"Lỗi khi xóa template: {e}")
                return False
            finally:
                cursor.close()
                connection.close()
        return False

    def generate_checksheet(self, template_id, measurements, output_path):
        """Tạo checksheet từ template và dữ liệu đo"""
        connection = self.db_config.get_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                # Lấy thông tin template
                cursor.execute("SELECT * FROM templates WHERE id = %s", (template_id,))
                template = cursor.fetchone()
                if not template:
                    return False

                # Load template
                wb = load_workbook(template['file_path'])
                ws = wb.active

                # Điền dữ liệu vào template
                for measurement in measurements:
                    # TODO: Implement logic điền dữ liệu vào template
                    # Cần xác định vị trí các ô trong template để điền dữ liệu
                    pass

                # Lưu file
                wb.save(output_path)
                return True
            except Exception as e:
                print(f"Lỗi khi tạo checksheet: {e}")
                return False
            finally:
                cursor.close()
                connection.close()
        return False

    def update_template(self, template_id, name):
        """Cập nhật thông tin template"""
        connection = self.db_config.get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE templates SET name = %s WHERE id = %s",
                    (name, template_id)
                )
                connection.commit()
                return True
            except Exception as e:
                print(f"Lỗi khi cập nhật template: {e}")
                return False
            finally:
                cursor.close()
                connection.close()
        return False 