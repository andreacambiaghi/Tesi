import re
import functions_file
import pandas as pd

def parse_function_call(condizione):
    pattern = r"(\w+)\((\w+)\)"
    matches = re.findall(pattern, condizione)

    for match in matches:
        function_name, column_name = match
        if hasattr(functions_file, function_name):
            return function_name, column_name

    return None, None

def evaluate_condition(condizione, df):
    try:
        function_name, column_name = parse_function_call(condizione)
        if function_name and column_name:
            function = getattr(functions_file, function_name)
            column = df[column_name]
            column = function(column)  # Valuta la funzione sulla colonna
            condizione = condizione.replace(function_name + f'({column_name})', f"column")

        column_names = df.columns.tolist()
        context = {col: df[col] for col in column_names}
        context['column'] = column
        context.update(functions_file.__dict__)  # Aggiungi le funzioni personalizzate al contesto

        return df[eval(condizione, context)]
    except (NameError, KeyError) as e:
        print("Errore: Nome di colonna non valido.")
        pattern = r"'(\w+)'"
        matches = re.findall(pattern, str(e))
        if matches:
            invalid_column = matches[-1]
            subexpression = re.search(r"(\([^()]+\))", condizione)
            if subexpression:
                print("Sottoespressione problematica:", subexpression.group(1))
        return pd.DataFrame()  # DataFrame vuoto per indicare un errore
    except Exception as e:
        print("Errore:", str(e))
        return pd.DataFrame()  # DataFrame vuoto per indicare un errore

# Caricamento del DataFrame da un file CSV
df = pd.read_csv('test.csv')

# Esempio di utilizzo
condizione = "Età > 30"
df_filtered = evaluate_condition(condizione, df)

print(df_filtered)
