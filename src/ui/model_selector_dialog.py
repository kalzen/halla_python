from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

class ModelSelectorDialog(QDialog):
    def __init__(self, models, current_model_id=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chọn Model")
        self.selected_model_id = None
        self.setFixedSize(380, 180)
        self.setStyleSheet('''
            QDialog {
                background: #fff;
                border-radius: 18px;
            }
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #b71c1c;
                margin-bottom: 8px;
            }
            QComboBox {
                border: 1px solid #e53935;
                border-radius: 10px;
                padding: 10px 18px;
                font-size: 16px;
                background: #f8fafc;
                color: #b71c1c;
            }
            QPushButton {
                background: #e53935;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 28px;
                font-size: 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #b71c1c;
            }
        ''')
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel("Chọn model:")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.combo = QComboBox()
        for m in models:
            self.combo.addItem(m['name'], m['id'])
        if current_model_id:
            idx = self.combo.findData(current_model_id)
            if idx >= 0:
                self.combo.setCurrentIndex(idx)
        layout.addWidget(self.combo)
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_ok = QPushButton("Chọn")
        btn_cancel = QPushButton("Hủy")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def get_selected_model_id(self):
        return self.combo.currentData() 