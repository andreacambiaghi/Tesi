from flask import Flask, render_template, jsonify, request
import subprocess
import pandas as pd
import io
import json
import ast
import sys
import os


import before_func as bf
import test_expr as te

import tempfile

# import atexit
from datetime import datetime


app = Flask(__name__)

node_dict = None
contenutoJSON = None

result = None
df = None  # Aggiunto DataFrame globale

def execute_script(data, nomeFileCSV):
    global df
    global node_dict
    try:
        arguments = [data, nomeFileCSV]

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(data)

        print("File temporaneo creato:", temp_file.name)

        #outputs = subprocess.check_output(['python', 'before_func.py'] + arguments).decode('utf-8')
        outputs = bf.preprocessing(temp_file.name, nomeFileCSV)
        outputDf = outputs[0]
        print(outputDf)
        node_dict_string = outputs[1]
        pd.set_option('display.max_rows', None)  # Imposta il numero massimo di righe a None
        pd.set_option('display.max_columns', None)
        df = pd.read_csv(io.StringIO(outputDf), sep=',')
        pd.reset_option('display.max_rows')
        pd.reset_option('display.max_columns')
        # node_dict = ast.literal_eval(node_dict_string)
        node_dict = {}

        node_dict_mask = eval(node_dict_string)

        for node_id, mask_string in node_dict_mask.items():
            mask_list = mask_string.strip().split(', ')
            mask_list = ["" if "False" in x else x for x in mask_list]  # Assegna stringa vuota al posto di "False"
            mask_series = pd.Series([bool(x) for x in mask_list], dtype=bool)  # Converte stringa vuota in False
            node_dict[node_id] = {"mask": mask_series}
            print(mask_list)

        print("NODEDICT", node_dict)
        print("DATAFRAME", df)
    except subprocess.CalledProcessError as e:
        print(f"Errore nell'esecuzione dello script: {e}")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['GET'])
def calculate():
    global result
    param = request.args.get('param')
    result = filter_dataframe(param)
    return jsonify({'result': result})


@app.route('/rowNode', methods=['GET'])
def rowNode():
    global result
    param = request.args.get('param')
    result = filter_dataframe(param)
    print(len(result))
    rows_count = str(len(result))
    return rows_count


@app.route('/save_json', methods=['POST'])
def save_json():
    global contenutoJSON
    json_data = request.form.get('json_data')
    contenutoJSON = json.loads(json_data)
    return jsonify({'status': 'success'})

@app.route('/run_script', methods=['POST'])
def run_script():
    json_data = request.form.get('json_data')
    nomeFileCSV = request.form.get('nomeFileCSV')
    data = json.loads(json_data)  # Analizza la stringa JSON in un oggetto Python
    print("Dati: ", data)
    execute_script(data, nomeFileCSV)  # Passa l'oggetto Python alla funzione execute_script
    print("Esecizione con successo")
    return jsonify({'status': 'success'})

def filter_dataframe(param):
    global df
    global node_dict
    filtered_df = df.copy()
    if param:
        filtered_df = df.loc[node_dict[param]["mask"]]

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    table_html = filtered_df.to_html(classes='table table-striped')
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    return table_html

@app.route('/run_scriptTest', methods=['GET'])
def run_scriptTest():
    param = request.args.get('param')
    nomeFileCSV = request.args.get('nomeFileCSV')
    arguments = [param, nomeFileCSV] + sys.argv[1:]
    try:
        print("ARGOMENTI: ", arguments)
        #output = subprocess.check_output(['python', 'test_expr.py'] + arguments).decode('utf-8')
        output = te.process_expr(arguments)
        print("output: ", output, "param: ", param)
        if "True" in output:
            return jsonify({'result': True})
        else:
            return jsonify({'result': False})
    except subprocess.CalledProcessError as e:
        print(f"Errore nell'esecuzione dello script: {e}")

@app.route('/crea_file_temporaneo', methods=['POST'])
def crea_file_temporaneo():
    try:
        contenuto = request.form.get('contenuto')
        print("CONTENUTO: " + contenuto)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        nome_file = f"file_temporaneo_{timestamp}.csv" 
        with open(nome_file, 'w', encoding='utf-8') as f:
            f.write(contenuto)

        # atexit.register(os.remove, nome_file)
        return jsonify(nome_file)

    except Exception as e:
        print("Errore durante la creazione del file temporaneo:", str(e))
        return "Errore durante la creazione del file temporaneo", 500


@app.route('/elimina_file_temporaneo', methods=['POST'])
def elimina_file_temporaneo():
    try:
        nome_file = request.form.get('nome_file')
        if os.path.exists(nome_file):
            os.remove(nome_file)
            return "File temporaneo eliminato con successo", 200
        else:
            return "Il file specificato non esiste", 404
    except Exception as e:
        print("Errore durante l'eliminazione del file temporaneo:", str(e))
        return "Errore durante l'eliminazione del file temporaneo", 500

if __name__ == '__main__':
    app.run(debug=True)