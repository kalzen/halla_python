from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
# Import model modules
try:
    from models.backup_manager import BackupManager
except ImportError:
    try:
        from src.models.backup_manager import BackupManager
    except ImportError:
        from ..models.backup_manager import BackupManager
import os

class BackupManagementWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.backup_manager = BackupManager()
        self.backup_dir = 'backups'
        os.makedirs(self.backup_dir, exist_ok=True)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Phần tạo backup
        backup_layout = QHBoxLayout()
        create_backup_btn = QPushButton("Tạo Bản Sao Lưu")
        create_backup_btn.clicked.connect(self.create_backup)
        
        backup_layout.addWidget(create_backup_btn)
        
        # Bảng danh sách backup
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(7)
        self.backup_table.setHorizontalHeaderLabels([
            "Thời gian",
            "Database",
            "Số Template",
            "Số Model",
            "Số Thông Số",
            "Số Đo",
            "Đường dẫn"
        ])
        
        # Nút khôi phục
        restore_btn = QPushButton("Khôi Phục")
        restore_btn.clicked.connect(self.restore_backup)
        
        # Thêm các layout vào layout chính
        layout.addLayout(backup_layout)
        layout.addWidget(self.backup_table)
        layout.addWidget(restore_btn)
        
        self.setLayout(layout)
        
        # Tải danh sách backup
        self.load_backups()
        
    def load_backups(self):
        """Tải danh sách backup vào bảng"""
        self.backup_table.setRowCount(0)
        backups = self.backup_manager.get_backups()
        for backup in backups:
            row = self.backup_table.rowCount()
            self.backup_table.insertRow(row)
            self.backup_table.setItem(row, 0, QTableWidgetItem(backup["timestamp"].strftime("%Y-%m-%d %H:%M:%S")))
            self.backup_table.setItem(row, 1, QTableWidgetItem(backup["path"]))
            
    def create_backup(self):
        """Tạo bản sao lưu mới"""
        backup_path = self.backup_manager.create_backup(self.backup_dir)
        if backup_path:
            QMessageBox.information(
                self,
                "Thành công",
                "Đã tạo bản sao lưu thành công"
            )
            self.load_backups()
        else:
            QMessageBox.critical(
                self,
                "Lỗi",
                "Không thể tạo bản sao lưu"
            )
            
    def restore_backup(self):
        """Khôi phục từ bản sao lưu"""
        selected_items = self.backup_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn bản sao lưu cần khôi phục")
            return
            
        backup_path = self.backup_table.item(selected_items[0].row(), 6).text()
        
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc chắn muốn khôi phục bản sao lưu này? Dữ liệu hiện tại sẽ bị xóa.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.backup_manager.restore_backup(backup_path):
                QMessageBox.information(
                    self,
                    "Thành công",
                    "Đã khôi phục bản sao lưu thành công"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Lỗi",
                    "Không thể khôi phục bản sao lưu"
                ) 