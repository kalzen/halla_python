import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='halla',
        port=3306
    )
    print('Kết nối thành công:', conn)
    conn.close()
except Exception as e:
    print('Lỗi:', e) 