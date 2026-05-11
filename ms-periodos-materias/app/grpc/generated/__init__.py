from pathlib import Path
import sys

_current_dir = Path(__file__).resolve().parent

if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))