import json
import pandas as pd
import sys
import codecs
import re
import functions_file


import importlib

importlib.reload(functions_file)






node_dict = None

def export_data():
    return node_dict

def find_node(node_id):
    return node_dict.get(node_id)

def parse_function_call(condizione):
    pattern = r"(\w+)\((\w+)\)"
    matches = re.findall(pattern, condizione)

    for match in matches:
        function_name, column_name = match
        if hasattr(functions_file, function_name):
            return function_name, column_name

    return None, None

def evaluate_condition(condizione, df):
    function_name, column_name = parse_function_call(condizione)
    column = None  # Inizializzazione di column a None
    if function_name and column_name:
        function = getattr(functions_file, function_name)
        column = df[column_name]
        column = function(column)  # Valuta la funzione sulla colonna
        condizione = condizione.replace(function_name + f'({column_name})', f"column")

    column_names = df.columns.tolist()
    context = {col: df[col] for col in column_names}
    context['column'] = column
    context.update(functions_file.__dict__)  # Aggiungi le funzioni personalizzate al contesto

    mask = pd.eval(condizione, engine='python', local_dict=context, parser='pandas')  # Valuta la condizione

    return mask


def test_mask(node, cond):
    maskApp = evaluate_condition(cond, df)
    #node_dict[node['id']]["cond"] = mask
    node_mask[node['id']]['cond'] = maskApp
    if node["type"] != "Foglia":
        if set(output["name"] for output in node["outputs"]) == {"Vero", "Falso"}:
            output_cond1 = cond + (" & " if cond else "") + "(" + node["value"] + ")"
            output_cond2 = cond + (" & " if cond else "") + "not (" + node["value"] + ")"
            if not df.eval(output_cond1).empty:
                test_mask(find_node(node["outputs"][0]['value']), output_cond1)
            if not df.eval(output_cond2).empty:
                test_mask(find_node(node["outputs"][1]['value']), output_cond2)
        else:
            for output in node["outputs"]:
                output_cond = cond + (" & " if cond else "") + "(" + node["value"] + ")" + " == '" + output["name"] + "'"
                if not df.eval(output_cond).empty:
                    test_mask(find_node(output["value"]), output_cond)
    else:
        # df.loc[df.eval(cond), "Risultato"] = node["value"]
        df.loc[mask, "Risultato"] = node["value"]



with open('grafo.json') as f:
   data = json.load(f)

#if len(sys.argv) > 1:

    #data = json.loads(sys.argv[1])

node_dict = {node["id"]: node for node in data}

df = pd.read_csv('test.csv')
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
df["Risultato"] = None

node_mask = {}

for node in data:
    node_mask[node['id']] = {}
    node_mask[node['id']]["cond"] = None

num_rows = len(df)
mask = pd.Series(False, index=range(num_rows))

for node in data:
    node_mask[node['id']]["cond"] = mask

first_col = df.columns[0]
start_node = next(node for node in data if node["type"] == "Start")
test_mask(start_node, "(" + df.columns[0] + " == " + df.columns[0] + ")")

# with pd.option_context('display.expand_frame_repr', False):
    # print(df)

pd.reset_option('display.max_rows')
pd.reset_option('display.max_columns')

# Stampa il dataframe in formato CSV
csv_data = df.to_csv(index=False)
# print(sys.argv[1])
# for key in node_dict.keys():
    # print(key)
node_mask_str = {}
for el in node_mask:
    app = ""
    for val in node_mask[el]['cond']:
        app = app + str(val) + ", "
    node_mask_str[el] = app

print(csv_data, "[########]", node_mask_str)