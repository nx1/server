import inspect
import importlib
import pkgutil
import sys

def get_all_installed_modules():
    modules = [module for module in sys.modules.keys()]
    modules = sorted(modules, key=lambda x: x.lower())
    return modules

def inspect(package_name):
    """
    Inspects a package recursively, printing its submodules and classes.
    package_name (string): The module object or the name e.g "matplotlib"
    """
    all_res = []    
    if 'flask' in package_name:
        return ['Can\'t inspect Flask modules recursively']

    try:
        module = importlib.import_module(package_name)
        module_name = module.__name__
        for k, v in module.__dict__.items():
            res = {"module_name"   : module_name,
                   "module"     : module,
                   "k"             : k,
                   "v"             : v}
            all_res.append(res)


    except Exception as e:
        ret = [f"{e.__class__.__name__}: {e}"]
        return ret

    return all_res
