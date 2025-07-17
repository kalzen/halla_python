from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog,
    QLineEdit, QFormLayout, QComboBox, QFileDialog
)
from PyQt6.QtCore import Qt
# Import model modules
try:
    from models.model_manager import ModelManager
except ImportError:
    try:
        from src.models.model_manager import ModelManager
    except ImportError:
        from ..models.model_manager import ModelManager
import os
import shutil
import threading

class AddModelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm Model Mới")
        self.setMinimumWidth(500)
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
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Tên Model:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel("Mô tả:"))
        self.desc_edit = QLineEdit()
        layout.addWidget(self.desc_edit)

        # Chọn hình ảnh
        img_layout = QHBoxLayout()
        self.img_path_edit = QLineEdit()
        self.img_path_edit.setPlaceholderText("Chọn hình ảnh...")
        img_btn = QPushButton("Chọn ảnh")
        img_btn.clicked.connect(self.choose_image)
        img_layout.addWidget(self.img_path_edit)
        img_layout.addWidget(img_btn)
        layout.addWidget(QLabel("Hình ảnh:"))
        layout.addLayout(img_layout)

        # Chọn template
        tpl_layout = QHBoxLayout()
        self.tpl_path_edit = QLineEdit()
        self.tpl_path_edit.setPlaceholderText("Chọn template...")
        tpl_btn = QPushButton("Chọn template")
        tpl_btn.clicked.connect(self.choose_template)
        tpl_layout.addWidget(self.tpl_path_edit)
        tpl_layout.addWidget(tpl_btn)
        layout.addWidget(QLabel("Template (xlsx):"))
        layout.addLayout(tpl_layout)

        # Thêm bảng thông số
        layout.addWidget(QLabel("Danh sách thông số cho model:"))
        self.param_table = QTableWidget(0, 3)
        self.param_table.setHorizontalHeaderLabels(["Tên thông số", "Đơn vị", "Mô tả"])
        layout.addWidget(self.param_table)

        # Nút thêm thông số
        add_param_btn = QPushButton("Thêm thông số")
        add_param_btn.clicked.connect(self.add_parameter)
        layout.addWidget(add_param_btn)

        # Nút lưu và hủy
        buttons = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        cancel_btn = QPushButton("Hủy")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def choose_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "Chọn hình ảnh", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file:
            self.img_path_edit.setText(file)

    def choose_template(self):
        file, _ = QFileDialog.getOpenFileName(self, "Chọn template", "", "Excel Files (*.xlsx)")
        if file:
            self.tpl_path_edit.setText(file)

    def add_parameter(self):
        """Thêm thông số mới"""
        dialog = AddParameterDialog(self)
        if dialog.exec():
            # Xử lý thêm thông số
            pass

    def get_model_info(self):
        return {
            'name': self.name_edit.text().strip(),
            'description': self.desc_edit.text().strip(),
            'image_path': self.img_path_edit.text().strip(),
            'template_path': self.tpl_path_edit.text().strip()
        }

class AddParameterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm Thông Số Mới")
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
        
        main_layout = QVBoxLayout(self)  # Thêm layout chính
        form_layout = QFormLayout()  # Layout cho form
        
        self.name_edit = QLineEdit()
        self.unit_edit = QLineEdit()
        self.description_edit = QLineEdit()
        
        form_layout.addRow("Tên Thông Số:", self.name_edit)
        form_layout.addRow("Đơn Vị:", self.unit_edit)
        form_layout.addRow("Mô tả:", self.description_edit)
        
        main_layout.addLayout(form_layout)  # Thêm form layout vào layout chính
        
        # Nút lưu và hủy
        buttons = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        cancel_btn = QPushButton("Hủy")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        main_layout.addLayout(buttons)

    def get_parameter_info(self):
        return {
            'name': self.name_edit.text().strip(),
            'unit': self.unit_edit.text().strip(),
            'description': self.description_edit.text().strip()
        }

class ModelManagementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Nút thêm model
        add_btn = QPushButton("Thêm Model Mới")
        add_btn.clicked.connect(self.add_model)
        layout.addWidget(add_btn)
        
        # Bảng danh sách model
        self.model_table = QTableWidget(0, 4)
        self.model_table.setHorizontalHeaderLabels(["ID", "Tên Model", "Mô tả", "Thao tác"])
        self.model_table.itemSelectionChanged.connect(self.on_model_selected)
        layout.addWidget(self.model_table)
        
        # Bảng danh sách thông số
        self.param_table = QTableWidget(0, 4)
        self.param_table.setHorizontalHeaderLabels(["ID", "Tên thông số", "Đơn vị", "Thao tác"])
        layout.addWidget(self.param_table)
        
        # Nút thêm thông số
        add_param_btn = QPushButton("Thêm Thông Số")
        add_param_btn.clicked.connect(self.add_parameter)
        layout.addWidget(add_param_btn)
        
        # Load dữ liệu
        self.load_models()

    def load_models(self):
        try:
            model_manager = ModelManager()
            models = model_manager.get_all_models()
            
            self.model_table.setRowCount(len(models))
            for i, model in enumerate(models):
                self.model_table.setItem(i, 0, QTableWidgetItem(str(model['id'])))
                self.model_table.setItem(i, 1, QTableWidgetItem(model['name']))
                self.model_table.setItem(i, 2, QTableWidgetItem(model['description']))
                
                # Nút xóa
                delete_btn = QPushButton("Xóa")
                delete_btn.clicked.connect(lambda checked, m=model: self.delete_model(m['id']))
                self.model_table.setCellWidget(i, 3, delete_btn)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách model: {str(e)}")

    def load_parameters(self, model_id):
        try:
            model_manager = ModelManager()
            parameters = model_manager.get_parameters(model_id)
            
            self.param_table.setRowCount(len(parameters))
            for i, param in enumerate(parameters):
                self.param_table.setItem(i, 0, QTableWidgetItem(str(param['id'])))
                self.param_table.setItem(i, 1, QTableWidgetItem(param['name']))
                self.param_table.setItem(i, 2, QTableWidgetItem(param['unit']))
                
                # Nút xóa
                delete_btn = QPushButton("Xóa")
                delete_btn.clicked.connect(lambda checked, p=param: self.delete_parameter(p['id']))
                self.param_table.setCellWidget(i, 3, delete_btn)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách thông số: {str(e)}")

    def on_model_selected(self):
        selected = self.model_table.selectedItems()
        if selected:
            model_id = int(self.model_table.item(selected[0].row(), 0).text())
            self.load_parameters(model_id)

    def add_model(self):
        dialog = AddModelDialog(self)
        if dialog.exec():
            try:
                model_info = dialog.get_model_info()
                model_manager = ModelManager()
                model_manager.add_model(model_info)
                self.load_models()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể thêm model: {str(e)}")

    def add_parameter(self):
        selected = self.model_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn model trước khi thêm thông số")
            return
            
        model_id = int(self.model_table.item(selected[0].row(), 0).text())
        dialog = AddParameterDialog(self)
        if dialog.exec():
            try:
                param_info = dialog.get_parameter_info()
                model_manager = ModelManager()
                model_manager.add_parameter(
                    model_id, 
                    param_info['name'], 
                    param_info['unit'], 
                    param_info['description']
                )
                self.load_parameters(model_id)
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể thêm thông số: {str(e)}")

    def delete_model(self, model_id):
        reply = QMessageBox.question(self, "Xác nhận", 
            "Bạn có chắc chắn muốn xóa model này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
        if reply == QMessageBox.StandardButton.Yes:
            try:
                model_manager = ModelManager()
                model_manager.delete_model(model_id)
                self.load_models()
                self.param_table.setRowCount(0)
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa model: {str(e)}")

    def delete_parameter(self, param_id):
        reply = QMessageBox.question(self, "Xác nhận", 
            "Bạn có chắc chắn muốn xóa thông số này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
        if reply == QMessageBox.StandardButton.Yes:
            try:
                model_manager = ModelManager()
                model_manager.delete_parameter(param_id)
                selected = self.model_table.selectedItems()
                if selected:
                    model_id = int(self.model_table.item(selected[0].row(), 0).text())
                    self.load_parameters(model_id)
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa thông số: {str(e)}") 