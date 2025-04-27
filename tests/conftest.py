# tests/conftest.py
import os
import sys
import pytest

# Añade src/ al path para poder importar packages
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
