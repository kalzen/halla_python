import os
import shutil

def clean_cache():
    """Xóa tất cả các file cache Python"""
    # Xóa thư mục __pycache__
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                cache_dir = os.path.join(root, dir_name)
                print(f"Xóa thư mục: {cache_dir}")
                shutil.rmtree(cache_dir)
        
        # Xóa file .pyc và .pyo
        for file_name in files:
            if file_name.endswith(('.pyc', '.pyo')):
                file_path = os.path.join(root, file_name)
                print(f"Xóa file: {file_path}")
                os.remove(file_path)

if __name__ == '__main__':
    clean_cache() 