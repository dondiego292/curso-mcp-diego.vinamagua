"""Configuración de pytest para resolver módulos desde la raíz del proyecto."""

import sys
from pathlib import Path

# Añadir la raíz de mi-proyecto-speckit al path de Python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
