import json
from colorama import Fore, Style, init

#inicializamos init
init()

# Diccionario en python
mision_python = {
    "ID": 244,
    "Título": "Mision secreta",
    "Estado": "En proceso",
    "Recompensa": "20 monedas"
}

# convertimos el diccionario a json
mision_json = json.dumps(mision_python, indent=4, ensure_ascii=False)

#guardamos el archivo en mision.json
with open("mision.json", "w", encoding='utf-8') as archivo:
    archivo.write(mision_json)

print(Fore.GREEN + "Se ha exportado correctamente" + Style.RESET_ALL)