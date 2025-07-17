import matplotlib
print(f"Matplotlib version: {matplotlib.__version__}")
print(f"Backend: {matplotlib.get_backend()}")
try:
    from matplotlib.backends.backend_qt6agg import FigureCanvasQTAgg
    print("Successfully imported backend_qt6agg")
except ImportError as e:
    print(f"Error importing backend_qt6agg: {e}") 