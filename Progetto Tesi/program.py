import tkinter as tk
from tkinter import filedialog, ttk
import os
import tempfile
import before_func as be
import shutil

def open_json_file():
    global json_file_path, json_button, confirm_button
    json_file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if json_file_path:
        json_button['text'] = f"File JSON: {os.path.basename(json_file_path)}"
        update_confirm_button_state()

def open_csv_file():
    global csv_file_path, csv_button, confirm_button
    csv_file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if csv_file_path:
        csv_button['text'] = f"File CSV: {os.path.basename(csv_file_path)}"
        update_confirm_button_state()

def update_confirm_button_state():
    if json_file_path and csv_file_path:
        confirm_button['state'] = 'normal'
    else:
        confirm_button['state'] = 'disabled'

def confirm_files():
    if json_file_path and csv_file_path:
        # Crea una copia dei file di input
        temp_json_path = tempfile.mktemp(suffix='.json')
        temp_csv_path = tempfile.mktemp(suffix='.csv')

        # Copia i file originali nei percorsi temporanei
        shutil.copyfile(json_file_path, temp_json_path)
        shutil.copyfile(csv_file_path, temp_csv_path)

        # Esegui il preprocessing utilizzando le copie dei file
        output = be.preprocessing(temp_json_path, temp_csv_path, program=True)
        print(output)

        # Elimina i file temporanei dopo l'uso
        os.remove(temp_json_path)
        os.remove(temp_csv_path)

        root.destroy()


root = tk.Tk()
root.title("Seleziona File")

frame = ttk.Frame(root)
frame.pack(padx=20, pady=10)

json_file_path = None
json_button = ttk.Button(frame, text="Seleziona file JSON con regole", command=open_json_file, style="TButton")
json_button.pack(padx=5, pady=5, fill=tk.X)

csv_file_path = None
csv_button = ttk.Button(frame, text="Seleziona file CSV con dati", command=open_csv_file, style="TButton")
csv_button.pack(padx=5, pady=5, fill=tk.X)

confirm_button = ttk.Button(frame, text="Conferma", command=confirm_files, state='disabled', style="TButton.Confirm.TButton")
confirm_button.pack(padx=5, pady=5, fill=tk.X)

style = ttk.Style(root)
style.configure("TButton", background="#FF5733")  # Imposta il colore di sfondo dei bottoni
style.map("TButton",
    background=[('active', '#FF8C00')])  # Cambia il colore quando il pulsante è attivo

style.configure("TButton.Confirm.TButton", background="#4CAF50")  # Imposta il colore di sfondo per il pulsante di conferma

root.mainloop()
