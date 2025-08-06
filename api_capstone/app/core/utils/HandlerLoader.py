import importlib
import pkgutil


def load_handlers(package):
    for mod in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        importlib.import_module(mod.name)
