# Hướng dẫn Build Ứng dụng Halla Measurement System

## Yêu cầu hệ thống
- Windows 10/11
- Python 3.8+
- MySQL Server

## Cách build ứng dụng

### Phương pháp 1: Sử dụng script tự động
```bash
# Chạy file build.bat
build.bat
```

### Phương pháp 2: Build thủ công
```bash
# 1. Kích hoạt virtual environment
.venv\Scripts\activate

# 2. Cài đặt dependencies
pip install -r requirements.txt

# 3. Build với PyInstaller
pyinstaller main.spec
```

## Kết quả
- File exe sẽ được tạo tại: `dist\main.exe`
- Kích thước: ~39MB
- Chạy độc lập, không cần cài đặt Python

## Cấu hình Database
Ứng dụng sử dụng cấu hình database mặc định:
- Host: https://cp121005.bkdata.vn
- User: bytes_halla
- Password: BoPzoM+CLFn=
- Database: bytes_halla
- Port: 3306

Để thay đổi cấu hình, tạo file `.env` với nội dung:
```
DB_HOST=your_host
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
DB_PORT=3306
```

## Thay đổi gần đây (v2.1)

### ✅ CẬP NHẬT: Dashboard và Dialog đo lường mới

**Cải tiến giao diện Dashboard:**
- Bỏ background của tất cả các label text để giao diện sạch hơn
- Cập nhật style cho image label với border dashed thay vì background màu

**Dialog đo lường mới với tính năng:**
- **Quét thiết bị tự động**: Tự động tìm và hiển thị các thiết bị COM có sẵn
- **Kết nối thiết bị**: Kết nối trực tiếp với thiết bị đo qua cổng COM
- **Chế độ nhập thủ công**: Nếu không có thiết bị, cho phép nhập giá trị bằng bàn phím
- **Hiển thị thông số**: Hiển thị tất cả thông số cần đo của model
- **Lưu kết quả**: Tự động lưu kết quả đo vào database
- **Giao diện hiện đại**: Style đồng nhất với toàn bộ ứng dụng

### ✅ SỬA LỖI: Import modules khi build PyInstaller (v2.0)

**Vấn đề trước đây:**
```
ModuleNotFoundError: No module named 'ui'
```

**Giải pháp đã áp dụng:**

1. **Cập nhật tất cả import statements** để hỗ trợ multiple import paths:
```python
# Pattern mới trong tất cả các file
try:
    from models.model_manager import ModelManager
except ImportError:
    try:
        from src.models.model_manager import ModelManager
    except ImportError:
        from ..models.model_manager import ModelManager
```

2. **Cải thiện main.spec** với đầy đủ hiddenimports:
```python
pathex=[
    os.path.abspath('.'),
    os.path.join(os.path.abspath('.'), 'src')
],
hiddenimports=[
    'src', 'src.config', 'src.ui', 'src.models', 'src.hardware',
    # ... và tất cả submodules
]
```

3. **Thêm sys.path configuration** trong main.py để đảm bảo import path đúng

## Troubleshooting

### ✅ Lỗi import modules (ĐÃ SỬA)
- **Trạng thái**: Đã được sửa hoàn toàn trong v2.0
- **Giải pháp**: Import paths đã được cải thiện để hoạt động với PyInstaller

### Lỗi "Access denied" khi build
```bash
# Đóng tất cả instances đang chạy
taskkill /f /im main.exe
# Sau đó build lại
pyinstaller main.spec
```

### Lỗi kết nối database
- Kiểm tra MySQL Server đang chạy
- Xác thực thông tin trong file .env
- Đảm bảo database 'halla' đã được tạo

## Lưu ý
- File exe có thể chạy trên máy không cài Python
- Cần kết nối internet để truy cập database
- Đảm bảo MySQL Server đang chạy và có thể truy cập được
- ⚠️ Warning "python_dotenv not found" có thể bỏ qua - không ảnh hưởng đến build 