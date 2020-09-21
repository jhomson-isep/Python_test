import datetime
url = "https://www.isep.com/cr/curso/maestria-en-educacion-especial/"

valor = url.find(".es")
fecha = datetime.datetime.now()
print(fecha - datetime.timedelta(hours=1))

telefono = '+52 1231231234'

if telefono[:3] in ('+52', '+57'):
    print(telefono[:3])

print(valor)
