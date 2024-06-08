import ast 
import importlib
import re
import pandas as pd
import sys


def find_functions(node):
    res = set()
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.Call):
            res.add(child.func.id)
        res |= find_functions(child)
    return res


def process_expr(args):
    df = pd.read_csv(args[1])

    #module_name = 'functions_file'
    #module = importlib.import_module(module_name)

    arguments = args[2:]
    modules = {}

    for arg in arguments:
        modules[arg[:-3]] = importlib.import_module(arg[:-3])

    #espressione = "(raddoppia(raddoppia(Età)) > raddoppia(60)) & ((aggiungi10(Salario) > 5000) | (Sesso == 'F'))"
    espressione = args[0]
    pt = ast.parse(espressione)

    name2func = {}

    for name in find_functions(pt):
        for module_name, module in modules.items():
            try:
                name2func[name] = getattr(module, name)
                break  # Se l'attributo viene trovato in un modulo, interrompi il ciclo
            except AttributeError:
                pass

        if name not in name2func:
            return "False"
            exit()

    try:
        df_ris = df.eval(espressione, resolvers=[name2func], engine='python')
        return "True"
    except Exception:
        return "False"
