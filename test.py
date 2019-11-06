import requests

#Registro 2 usuarios
url='http://0.0.0.0:5000/register'
x = requests.post(url, json= {"nombre":"alejandro1","email":"alejandro1@gmail.com","contrasena":"alejandro123"})
print(x.json())

url='http://0.0.0.0:5000/register'
x = requests.post(url, json= {"nombre":"alejandro2","email":"alejandro2@gmail.com","contrasena":"alejandro123"})
print(x.json())

#Me logeo con los 2
url='http://0.0.0.0:5000/login'
x = requests.get(url, json= {"email":"alejandro1@gmail.com","contrasena":"alejandro123"})
token1={'x-access-token': x.json()['token']}
print(x.json())

url='http://0.0.0.0:5000/login'
x = requests.get(url, json= {"email":"alejandro2@gmail.com","contrasena":"alejandro123"})
token2={'x-access-token': x.json()['token']}
print(x.json())

#Creo un cuestionario
url='http://0.0.0.0:5000/cuestionario'
x = requests.post(url, headers=token1, json= {"titulo" : "Cuestionario sobre cosas basicas" , "preguntas": [ { "pregunta": "Que es una naranja", "opciones":["un color", "una fruta", "las 2 cosas", "un animal"], "tipo": "Test", "solucion": ["0","0","1","0"] },{ "pregunta": "Donde viven los tiburones", "opciones":["en la selva", "debajo de la tierra", "en casas", "en el mar"],"tipo": "Ponderada", "solucion": ["0","-1","-2","1"] } ]})
print(x.json())
#Muestro los cuestionarios
url='http://0.0.0.0:5000/cuestionarios'
x = requests.get(url)
print(x.json())
#Intento borrarlo con el que no lo creo
url='http://0.0.0.0:5000/cuestionario/1'
x = requests.delete(url, headers=token2)
print(x.json())
#Lo borro con el que lo creo
url='http://0.0.0.0:5000/cuestionario/1'
x = requests.delete(url, headers=token1)
print(x.json())
#Vuelvo a crearlo
url='http://0.0.0.0:5000/cuestionario'
x = requests.post(url, headers=token1, json= { "titulo" : "Cuestionario sobre cosas basicas" , "preguntas": [ { "pregunta": "Que es una naranja", "opciones":["un color", "una fruta", "las 2 cosas", "un animal"], "tipo": "Test", "solucion": ["0","0","1","0"] },{ "pregunta": "Donde viven los tiburones", "opciones":["en la selva", "debajo de la tierra", "en casas", "en el mar"],"tipo": "Ponderada", "solucion": ["0","-1","-2","1"] } ]})
print(x.json())
#Muestro los cuestionarios
url='http://0.0.0.0:5000/cuestionarios'
x = requests.get(url)
print(x.json())
#Lo inicio con los 2
url='http://0.0.0.0:5000/resolver/1'
x = requests.post(url, headers=token1)
print(x.json())

url='http://0.0.0.0:5000/resolver/1'
x = requests.post(url, headers=token2)
print(x.json())
#Lo resuelvo con los 2
url='http://0.0.0.0:5000/opcion'
x = requests.post(url, headers=token1, json={"opcion": "en casas","id_usuariocuestionario": "1","pregunta": "Donde viven los tiburones"})
print(x.json())

url='http://0.0.0.0:5000/opcion'
x = requests.post(url, headers=token1, json={"opcion": "las 2 cosas","id_usuariocuestionario": "1","pregunta": "Que es una naranja"})
print(x.json())

url='http://0.0.0.0:5000/opcion'
x = requests.post(url, headers=token2, json={"opcion": "en casas","id_usuariocuestionario": "2","pregunta": "Donde viven los tiburones"})
print(x.json())

url='http://0.0.0.0:5000/opcion'
x = requests.post(url, headers=token2, json={"opcion": "las 2 cosas","id_usuariocuestionario": "2","pregunta": "Que es una naranja"})
print(x.json())
#Obtengo los resultados con los 2
url='http://0.0.0.0:5000/cuestionario/resultados'
x = requests.get(url, headers=token1)
print(x.json())

url='http://0.0.0.0:5000/cuestionario/resultados'
x = requests.get(url, headers=token2)
print(x.json())
#Vuelvo a hacerlo con el 1
url='http://0.0.0.0:5000/resolver/1'
x = requests.post(url, headers=token1)
print(x.json())

url='http://0.0.0.0:5000/opcion'
x = requests.post(url, headers=token1, json={"opcion": "en el mar","id_usuariocuestionario": "3","pregunta": "Donde viven los tiburones"})
print(x.json())

url='http://0.0.0.0:5000/opcion'
x = requests.post(url, headers=token1, json={"opcion": "las 2 cosas","id_usuariocuestionario": "3","pregunta": "Que es una naranja"})
print(x.json())
#Obtengo los resultados del 1
url='http://0.0.0.0:5000/cuestionario/resultados'
x = requests.get(url, headers=token1)
print(x.json())

