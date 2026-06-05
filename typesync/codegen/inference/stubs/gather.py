import importlib
import pathlib
import sys
from types import ModuleType


BASE_DIR = pathlib.Path(__file__).resolve().parent
STUBBED_MODULES = [
    obj.name
    for obj in BASE_DIR.glob("*")
    if obj.is_dir()
]


def get_stub_module(module: str) -> ModuleType | None:
    stub_parent_dir = str(BASE_DIR.parent)
    sys.path.insert(0, stub_parent_dir)
    try:
        return importlib.import_module("."+module, "stubs")
    except ImportError:
        return None
    finally:
        sys.path.remove(stub_parent_dir)
