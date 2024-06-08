import json
import pandas as pd
import sys
import importlib
import os
import csv
import ast

def preprocessing(json_data, csv_path, program = False):
    node_dict = None

    def transform_json(data2):
        result = []
        for el in data2['nodes']:
            new_id = el['id']
            new_name = el['name']
            interfaces = el.get('interfaces', [])
            has_input = any(interface[0] == 'Input' for interface in interfaces)
            if has_input and len(interfaces) == 1:
                new_type = 'Foglia'
            elif has_input and len(interfaces) > 1:
                new_type = 'Nodo'
            else:
                new_type = 'Start'
            new_options = el['options'][0][1]
            outputs = []
            for interface in interfaces:
                if interface[0] != 'Input':
                    value = None
                    for connection in data2['connections']:
                        if connection['from'] == interface[1]['id']:
                            to_id = connection['to']
                            for node in data2['nodes']:
                                if new_type != "Foglia" and node['interfaces'][-1][1]['id'] == to_id:
                                    value = node['id']
                                    break
                        elif connection['to'] == interface[1]['id']:
                            from_id = connection['from']
                            for node in data2['nodes']:
                                if new_type != "Foglia" and node['interfaces'][-1][1]['id'] == from_id:
                                    value = node['id']
                                    break 
                    output = {'name': interface[0], 'value': value}
                    outputs.append(output)
            if new_type != "Foglia":
                new_element = {'id': new_id,
                    'name': new_name,
                    "type": new_type,
                    'value': new_options,
                    'outputs': outputs}
            else:
                new_element = {'id': new_id,
                    'name': new_name,
                    "type": new_type,
                    'value': new_options}
            result.append(new_element)

        return result

    def find_functions(node):
        res = set()
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Call):
                res.add(child.func.id)
            res |= find_functions(child)
        return res

    def export_data():
        return node_dict

    def find_node(node_id):
        return node_dict.get(node_id)

    def test_mask(node, cond):
        node_dict[node['id']]["cond"] = cond
        pt = ast.parse(cond)
        name2func = {name: getattr(module, name) for name in find_functions(pt)}
        mask = df.eval(cond, resolvers=[name2func], engine='python')
        node_mask[node['id']]['cond'] = mask
        if node["type"] != "Foglia":
            if set(output["name"] for output in node["outputs"]) == {"Vero", "Falso"}:
                output_cond1 = cond + (" & " if cond else "") + "(" + node["value"] + ")"
                output_cond2 = cond + (" & " if cond else "") + "(not (" + node["value"] + "))"
                test_mask(find_node(node["outputs"][0]['value']), output_cond1)
                test_mask(find_node(node["outputs"][1]['value']), output_cond2)
            elif node["outputs"] and node["outputs"][0]["name"].startswith("x"):
                for output in node["outputs"]:
                    output_name = cond + (" & " if cond else "") + "(" + output["name"].replace("x", node["value"]) + ")"
                    test_mask(find_node(output["value"]), output_name)
            else:
                for output in node["outputs"]:
                    if output["name"] != "_Altro":
                        output_cond = cond + (" & " if cond else "") + "(" + node["value"] + ")" + " == '" + output["name"] + "'"
                        test_mask(find_node(output["value"]), output_cond)
                    else:
                        other = ""
                        for el in node["outputs"][:-1]:
                            other = other + (" & " if other else "") + "(" + node["value"] + " != '" + el['name'] + "')"
                        output_cond = cond + "& (" + other + ")"
                        test_mask(find_node(output["value"]), output_cond)
        else:
            df.loc[mask, "Risultato"] = node["value"]

    # Read CSV file
    df = pd.read_csv(csv_path)

    # Import custom functions from module
    module_name = 'functions_file'
    module = importlib.import_module(module_name)

    # Transform JSON data
    if not program:
        #data = json.loads(json_data)
        with open(json_data, 'r') as file:
            data = json.load(file)
    else:
        if not os.path.isfile(json_data):
            print("Errore: Il file specificato non esiste")
            sys.exit(1)
        with open(json_data, 'r') as f:
            json_string = f.read()
            app = json.loads(json_string)
            res = transform_json(app) 
            data = json.loads(json.dumps(res))

    # Create node dictionary
    node_dict = {node["id"]: node for node in data}

    # Initialize node mask dictionary
    node_mask = {}
    for node in data:
        node_mask[node['id']] = {}
        node_mask[node['id']]["cond"] = None

    num_rows = len(df)
    mask = pd.Series(False, index=range(num_rows))

    # Create initial mask
    for node in data:
        node_mask[node['id']]["cond"] = mask

    # Set the first column of the DataFrame as the starting condition
    first_col = df.columns[0]
    start_node = next(node for node in data if node["type"] == "Start")
    test_mask(start_node, "(" + df.columns[0] + " == " + df.columns[0] + ")")

    # Set pandas display options
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    df["Risultato"] = None

    # Set initial conditions for nodes
    for node in data:
        node_dict[node['id']]["cond"] = "False"

    # Run the mask tests
    start_node = next(node for node in data if node["type"] == "Start")
    test_mask(start_node, "(" + df.columns[0] + " == " + df.columns[0] + ")")

    # Reset pandas display options
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')

    # Convert DataFrame to CSV format
    csv_data = df.to_csv(index=False)

    # Create node mask string dictionary
    node_mask_str = {}
    for el in node_mask:
        app = ""
        for val in node_mask[el]['cond']:
            app = app + str(val) + ", "
        node_mask_str[el] = app

    # Return the processed CSV data and node masks
    if not program:
        result_tuple = (str(csv_data), str(node_mask_str))
        return result_tuple
    else:
        file_path = "output.csv"
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(df.columns)
            writer.writerows(df.values)
        return csv_data

# Example usage:
# csv_data, node_mask_str = preprocessing('grafo.json', 'data.csv')
# print(csv_data)
# print(node_mask_str)
