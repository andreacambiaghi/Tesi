from flask import Flask, render_template, request, jsonify
import os
import tempfile
import shutil
import before_func as be  # Assicurati che before_func sia nel tuo percorso di ricerca

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('indexProgram.html')

@app.route('/process_files', methods=['POST'])
def process_files():
    json_file = request.files['jsonData']
    csv_file = request.files['csvData']

    # Crea file temporanei per memorizzare i dati dei file
    temp_json_path = tempfile.mktemp(suffix='.json')
    temp_csv_path = tempfile.mktemp(suffix='.csv')

    # Scrivi i dati dei file temporanei
    with open(temp_json_path, 'wb') as f:
        f.write(json_file.read())
    with open(temp_csv_path, 'wb') as f:
        f.write(csv_file.read())

    # Esegui il preprocessing utilizzando i file temporanei
    output = be.preprocessing(temp_json_path, temp_csv_path, program=True)

    # Stampa il risultato del preprocessing
    print("Risultato del preprocessing:")
    print(output)

    # Elimina i file temporanei
    os.remove(temp_json_path)
    os.remove(temp_csv_path)

    # Restituisci una risposta al client con il risultato del preprocessing
    response_data = {
        'message': 'I file sono stati processati correttamente.',
        'status': 'success',
        'table': output  # Aggiungi il risultato come parte della risposta
    }
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
