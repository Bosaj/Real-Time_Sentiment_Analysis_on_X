import os
import runpy

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
runpy.run_path(os.path.join(CURRENT_DIR, "app.py"), run_name="__main__")
