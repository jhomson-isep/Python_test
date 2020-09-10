url = "https://www.isep.com/cr/curso/maestria-en-educacion-especial/"

valor = url.find(".es")

telefono = '+521231231234'

if telefono[:3] in ('+52', '+57'):
    print(telefono[:3])

print(valor)
