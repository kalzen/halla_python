from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog,
    QLineEdit, QFileDialog
)
from PyQt6.QtCore import Qt

# Import model modules
try:
    from models.template_manager import TemplateManager
except ImportError:
    try:
        from src.models.template_manager import TemplateManager
    except ImportError:
        from ..models.template_manager import TemplateManager
import os
import shutil

class AddTemplateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm Template Mới")
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background: #f8fafc;
            }
            QLabel {
                color: #1e293b;
                font-size: 14px;
            }
            QPushButton {
                background: #e53935;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #b71c1c;
            }
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 16px;
                background: white;
            }
            QLineEdit:hover {
                border-color: #e53935;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Tên template
        layout.addWidget(QLabel("Tên Template:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        # Chọn file
        file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Chọn file template...")
        file_btn = QPushButton("Chọn file")
        file_btn.clicked.connect(self.choose_file)
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(file_btn)
        layout.addWidget(QLabel("File Template:"))
        layout.addLayout(file_layout)
        
        # Nút lưu và hủy
        buttons = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        cancel_btn = QPushButton("Hủy")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
        
    def choose_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file template",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        if file:
            self.file_path_edit.setText(file)
            
    def get_template_info(self):
        """Lấy thông tin template"""
        return {
            'name': self.name_edit.text(),
            'file_path': self.file_path_edit.text()
        }

class TemplateManagementWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.template_manager = TemplateManager()
        self.setStyleSheet("""
            QWidget {
                background: #f8fafc;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #1e293b;
                font-size: 14px;
            }
            QPushButton {
                background: #e53935;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #b71c1c;
            }
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QTableWidget::item:selected {
                background: #fecaca;
                color: #b71c1c;
            }
            QHeaderView::section {
                background: #f8fafc;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                font-weight: 600;
            }
        """)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Phần quản lý template
        template_layout = QVBoxLayout()
        template_header = QHBoxLayout()
        
        template_label = QLabel("Danh sách Template")
        add_template_btn = QPushButton("Thêm Template")
        add_template_btn.clicked.connect(self.add_template)
        
        template_header.addWidget(template_label)
        template_header.addWidget(add_template_btn)
        
        self.template_table = QTableWidget()
        self.template_table.setColumnCount(3)
        self.template_table.setHorizontalHeaderLabels(["ID", "Tên Template", "Đường dẫn"])
        
        template_layout.addLayout(template_header)
        template_layout.addWidget(self.template_table)
        
        # Thêm nút xóa template
        delete_btn = QPushButton("Xóa Template")
        delete_btn.clicked.connect(self.delete_template)
        template_layout.addWidget(delete_btn)
        
        layout.addLayout(template_layout)
        self.setLayout(layout)
        
        # Tải danh sách template
        self.load_templates()
        
    def load_templates(self):
        """Tải danh sách template"""
        templates = self.template_manager.get_all_templates()
        self.template_table.setRowCount(len(templates))
        
        for i, template in enumerate(templates):
            self.template_table.setItem(i, 0, QTableWidgetItem(str(template['id'])))
            self.template_table.setItem(i, 1, QTableWidgetItem(template['name']))
            self.template_table.setItem(i, 2, QTableWidgetItem(template['file_path']))
            
    def add_template(self):
        """Thêm template mới"""
        dialog = AddTemplateDialog(self)
        if dialog.exec():
            info = dialog.get_template_info()
            if not info['name'] or not info['file_path']:
                QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin!")
                return
                
            # Copy file template vào thư mục riêng
            tpl_dir = "static/templates"
            os.makedirs(tpl_dir, exist_ok=True)
            tpl_save = os.path.join(tpl_dir, os.path.basename(info['file_path']))
            shutil.copy2(info['file_path'], tpl_save)
            
            # Lưu vào database
            if self.template_manager.add_template(info['name'], tpl_save):
                self.load_templates()
                QMessageBox.information(self, "Thành công", "Đã thêm template mới!")
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể thêm template!")
                
    def delete_template(self):
        """Xóa template"""
        selected_items = self.template_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn template cần xóa")
            return
            
        template_id = int(self.template_table.item(selected_items[0].row(), 0).text())
        
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc chắn muốn xóa template này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.template_manager.delete_template(template_id):
                self.load_templates()
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể xóa template") 