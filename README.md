# Hệ thống Đo lường và Báo cáo

Hệ thống phần mềm quản lý đo lường và báo cáo tự động cho thiết bị High Gauge.

## Tính năng chính

- Quản lý model và thông số đo
- Kết nối và đo lường với thiết bị High Gauge
- Dashboard hiển thị biểu đồ lịch sử đo
- Xuất báo cáo và checksheet theo template

## Cài đặt

1. Cài đặt Python 3.8 trở lên
2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

## Cấu hình

1. Tạo file `.env` trong thư mục gốc với các thông tin sau:
```
DB_HOST=your_database_host
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=your_database_name
```

## Chạy chương trình

```bash
python src/main.py
```