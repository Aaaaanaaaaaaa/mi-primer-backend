import requests

url = "https://pokeapi.co/api/v2/pokemon/pikachu"
respuesta = requests.get(url)

# Comprobamos que la respuesta es exitosa
if respuesta.status_code == 200:
    print("la petición fue exitosa")
    datos = respuesta.json()
    print(f"Nombre: {datos['name']} Peso: {datos['weight']}")
else:
    print("Hubo un error en al petición")