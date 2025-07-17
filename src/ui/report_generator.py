from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QDateEdit, QFileDialog, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, QDate

# Import model modules
try:
    from models.report_manager import ReportManager
    from models.model_manager import ModelManager
except ImportError:
    try:
        from src.models.report_manager import ReportManager
        from src.models.model_manager import ModelManager
    except ImportError:
        from ..models.report_manager import ReportManager
        from ..models.model_manager import ModelManager

class ReportGeneratorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.report_manager = ReportManager()
        self.model_manager = ModelManager()
        self.current_excel_path = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Phần chọn template
        template_layout = QHBoxLayout()
        template_label = QLabel("Chọn Template:")
        self.template_combo = QComboBox()
        self.load_templates()
        
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.template_combo)
        
        # Phần chọn model
        model_layout = QHBoxLayout()
        model_label = QLabel("Chọn Model:")
        self.model_combo = QComboBox()
        self.load_models()
        
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        
        # Phần chọn thời gian
        date_layout = QHBoxLayout()
        
        start_date_label = QLabel("Từ ngày:")
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        
        end_date_label = QLabel("Đến ngày:")
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        
        date_layout.addWidget(start_date_label)
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(end_date_label)
        date_layout.addWidget(self.end_date)
        
        # Nút tạo báo cáo
        generate_btn = QPushButton("Tạo Báo Cáo")
        generate_btn.clicked.connect(self.generate_report)
        
        # Phần xuất file
        export_group = QGroupBox("Xuất Báo Cáo")
        export_layout = QVBoxLayout()
        
        # Nút xuất PDF
        pdf_btn = QPushButton("Xuất PDF")
        pdf_btn.clicked.connect(self.export_to_pdf)
        pdf_btn.setEnabled(False)
        self.pdf_btn = pdf_btn
        
        # Nút xuất CSV
        csv_btn = QPushButton("Xuất CSV")
        csv_btn.clicked.connect(self.export_to_csv)
        csv_btn.setEnabled(False)
        self.csv_btn = csv_btn
        
        export_layout.addWidget(pdf_btn)
        export_layout.addWidget(csv_btn)
        export_group.setLayout(export_layout)
        
        # Thêm các layout vào layout chính
        layout.addLayout(template_layout)
        layout.addLayout(model_layout)
        layout.addLayout(date_layout)
        layout.addWidget(generate_btn)
        layout.addWidget(export_group)
        
        self.setLayout(layout)
        
    def load_templates(self):
        """Tải danh sách template"""
        templates = self.report_manager.get_report_templates()
        self.template_combo.clear()
        
        for template in templates:
            self.template_combo.addItem(template['name'], template['id'])
            
    def load_models(self):
        """Tải danh sách model"""
        models = self.model_manager.get_all_models()
        self.model_combo.clear()
        
        for model in models:
            self.model_combo.addItem(model['name'], model['id'])
            
    def generate_report(self):
        """Tạo báo cáo"""
        template_id = self.template_combo.currentData()
        model_id = self.model_combo.currentData()
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        
        if not template_id or not model_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn template và model")
            return
            
        # Chọn nơi lưu file
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu Báo Cáo",
            "",
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            if self.report_manager.generate_report(
                template_id,
                model_id,
                start_date,
                end_date,
                file_path
            ):
                self.current_excel_path = file_path
                self.pdf_btn.setEnabled(True)
                self.csv_btn.setEnabled(True)
                QMessageBox.information(
                    self,
                    "Thành công",
                    "Đã tạo báo cáo thành công"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Lỗi",
                    "Không thể tạo báo cáo"
                )
                
    def export_to_pdf(self):
        """Xuất báo cáo ra PDF"""
        if not self.current_excel_path:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu File PDF",
            "",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            if self.report_manager.export_to_pdf(
                self.current_excel_path,
                file_path
            ):
                QMessageBox.information(
                    self,
                    "Thành công",
                    "Đã xuất báo cáo ra PDF thành công"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Lỗi",
                    "Không thể xuất báo cáo ra PDF"
                )
                
    def export_to_csv(self):
        """Xuất báo cáo ra CSV"""
        if not self.current_excel_path:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu File CSV",
            "",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            if self.report_manager.export_to_csv(
                self.current_excel_path,
                file_path
            ):
                QMessageBox.information(
                    self,
                    "Thành công",
                    "Đã xuất báo cáo ra CSV thành công"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Lỗi",
                    "Không thể xuất báo cáo ra CSV"
                ) 