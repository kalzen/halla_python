import os
import sys
import time
import threading
import subprocess
import signal
import psutil
import shutil
from pathlib import Path

class AppReloader:
    def __init__(self):
        self.process = None
        self.running = True
        self.restart_app()
        self.watch_thread = threading.Thread(target=self.watch_files)
        self.watch_thread.daemon = True
        self.watch_thread.start()

    def restart_app(self):
        # Kill existing process if any
        if self.process:
            try:
                parent = psutil.Process(self.process.pid)
                children = parent.children(recursive=True)
                for child in children:
                    child.kill()
                parent.kill()
            except:
                pass

        # Clear cache directories
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in dirs:
                cache_dir = os.path.join(root, '__pycache__')
                print(f"Xóa thư mục cache: {cache_dir}")
                shutil.rmtree(cache_dir)

        # Set environment variables to disable caching
        os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.environ['QT_LOGGING_RULES'] = '*.debug=false'
        os.environ['PLOTLY_RENDERER'] = 'browser'

        # Start the application
        print("\nKhởi động lại ứng dụng...")
        self.process = subprocess.Popen([sys.executable, 'src/main.py'])

    def watch_files(self):
        """Theo dõi thay đổi file Python"""
        last_modified = {}
        while self.running:
            for py_file in Path('.').rglob('*.py'):
                try:
                    mtime = py_file.stat().st_mtime
                    if py_file in last_modified and mtime > last_modified[py_file]:
                        print(f"\nPhát hiện thay đổi trong file: {py_file}")
                        self.restart_app()
                    last_modified[py_file] = mtime
                except:
                    pass
            time.sleep(1)

def main():
    # Add src directory to Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Create and start the reloader
    reloader = AppReloader()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        reloader.running = False
        if reloader.process:
            reloader.process.terminate()
        reloader.watch_thread.join()

if __name__ == '__main__':
    main() 