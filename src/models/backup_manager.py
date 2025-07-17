import os
import shutil
import json
from datetime import datetime

# Import config modules
try:
    from config.database import DatabaseConfig
except ImportError:
    try:
        from src.config.database import DatabaseConfig
    except ImportError:
        from ..config.database import DatabaseConfig

class BackupManager:
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.backup_dir = "backups"
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def create_backup(self):
        """Tạo bản sao lưu mới"""
        try:
            # Tạo tên file backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
            os.makedirs(backup_path)

            # Sao lưu database
            db_backup = {
                "models": self._get_table_data("models"),
                "parameters": self._get_table_data("parameters"),
                "measurements": self._get_table_data("measurements"),
                "templates": self._get_table_data("templates")
            }

            # Lưu dữ liệu database
            with open(os.path.join(backup_path, "database.json"), "w", encoding="utf-8") as f:
                json.dump(db_backup, f, ensure_ascii=False, indent=2)

            # Sao lưu templates
            templates_dir = os.path.join(backup_path, "templates")
            os.makedirs(templates_dir)
            for template in db_backup["templates"]:
                if os.path.exists(template["file_path"]):
                    shutil.copy2(template["file_path"], templates_dir)

            return True
        except Exception as e:
            print(f"Lỗi khi tạo backup: {e}")
            return False

    def restore_backup(self, backup_path):
        """Khôi phục từ bản sao lưu"""
        try:
            # Đọc dữ liệu database
            with open(os.path.join(backup_path, "database.json"), "r", encoding="utf-8") as f:
                db_backup = json.load(f)

            # Khôi phục database
            self._restore_table_data("models", db_backup["models"])
            self._restore_table_data("parameters", db_backup["parameters"])
            self._restore_table_data("measurements", db_backup["measurements"])
            self._restore_table_data("templates", db_backup["templates"])

            # Khôi phục templates
            templates_dir = os.path.join(backup_path, "templates")
            if os.path.exists(templates_dir):
                for template in db_backup["templates"]:
                    if os.path.exists(template["file_path"]):
                        shutil.copy2(
                            os.path.join(templates_dir, os.path.basename(template["file_path"])),
                            template["file_path"]
                        )

            return True
        except Exception as e:
            print(f"Lỗi khi khôi phục backup: {e}")
            return False

    def get_backups(self):
        """Lấy danh sách các bản sao lưu"""
        backups = []
        for item in os.listdir(self.backup_dir):
            backup_path = os.path.join(self.backup_dir, item)
            if os.path.isdir(backup_path) and item.startswith("backup_"):
                try:
                    timestamp = datetime.strptime(item[7:], "%Y%m%d_%H%M%S")
                    backups.append({
                        "timestamp": timestamp,
                        "path": backup_path
                    })
                except:
                    continue
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)

    def _get_table_data(self, table_name):
        """Lấy dữ liệu từ một bảng"""
        connection = self.db_config.get_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(f"SELECT * FROM {table_name}")
                return cursor.fetchall()
            finally:
                cursor.close()
                connection.close()
        return []

    def _restore_table_data(self, table_name, data):
        """Khôi phục dữ liệu vào một bảng"""
        if not data:
            return

        connection = self.db_config.get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                # Xóa dữ liệu cũ
                cursor.execute(f"DELETE FROM {table_name}")
                # Thêm dữ liệu mới
                for row in data:
                    columns = ", ".join(row.keys())
                    placeholders = ", ".join(["%s"] * len(row))
                    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    cursor.execute(query, list(row.values()))
                connection.commit()
            finally:
                cursor.close()
                connection.close() 