from importlib import import_module


def load_object(path):
    """
    Load an object given its absolute object path, and return it.

    object can be the import path of a class, function, variable or an
    instance, e.g. "bifrost.service.bifrost.BifrostService"
    """
    module, name = path.rsplit(".", 1)
    mod = import_module(module)

    return getattr(mod, name)
