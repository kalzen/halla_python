import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
import mysql.connector

app = QApplication(sys.argv)
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='halla',
        port=3306
    )
    QMessageBox.information(None, 'Kết nối DB', 'Kết nối MySQL thành công!')
    conn.close()
except Exception as e:
    QMessageBox.critical(None, 'Kết nối DB', f'Lỗi: {e}')
sys.exit(app.exec()) 